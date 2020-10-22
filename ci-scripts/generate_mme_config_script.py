#/*
# * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
# * contributor license agreements.  See the NOTICE file distributed with
# * this work for additional information regarding copyright ownership.
# * The OpenAirInterface Software Alliance licenses this file to You under
# * the OAI Public License, Version 1.1  (the "License"); you may not use this file
# * except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *	  http://www.openairinterface.org/?page_id=698
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *-------------------------------------------------------------------------------
# * For more information about the OpenAirInterface (OAI) Software Alliance:
# *	  contact@openairinterface.org
# */
#---------------------------------------------------------------------

import os
import re
import sys
import ipaddress

class mmeConfigGen():
	def __init__(self):
		self.kind = ''
		self.hss_s6a_IP = ''
		self.mme_s6a_IP = ''
		self.mme_s1c_IP = ''
		self.mme_s1c_name = ''
		self.mme_s10_IP = ''
		self.mme_s10_name = ''
		self.mme_s11_IP = ''
		self.mme_s11_name = ''
		self.spgwc0_s11_IP = ''
		self.mme_gid = ''
		self.mme_code = ''
		self.mcc = ''
		self.mnc = ''
		self.tai_list = ""
		self.realm = ''
		self.prefix = ''
		self.fromDockerFile = False

	def GenerateMMEConfigurer(self):
		# We cannot have S10 and S11 sharing the same interface and the same IP address since they are using the same port
		useLoopBackForS10 = False
		if (self.mme_s10_name == self.mme_s11_name) and (str(self.mme_s10_IP) == str(self.mme_s11_IP)):
			print ('Using the same interface name and the same IP address for S11 and S10 is not allowed.')
			print ('Starting a virtual interface on loopback for S10')
			useLoopBackForS10 = True

		tais = self.tai_list.split(',')
		mme_conf_file = open('./mme.conf', 'w')
		mme_conf_file.write('# generated by generate_mme_config_script.py\n')
		mme_conf_file.write('MME : \n')
		mme_conf_file.write('{\n')
		mme_conf_file.write('  REALM = "'+self.realm+'";\n')
		mme_conf_file.write('  INSTANCE = 0;\n')
		mme_conf_file.write('  PID_DIRECTORY = "/var/run";\n')
		mme_conf_file.write('  MAX_S1_ENB = 8; # power of 2\n')
		mme_conf_file.write('  MAX_UE = 1024;# power of 2\n')
		mme_conf_file.write('  RELATIVE_CAPACITY = 10;\n')
		mme_conf_file.write('  EMERGENCY_ATTACH_SUPPORTED = "no";\n')
		mme_conf_file.write('  UNAUTHENTICATED_IMSI_SUPPORTED = "no";\n')
		mme_conf_file.write('  DUMMY_HANDOVER_FORWARDING_ENABLED = "yes";\n')
		mme_conf_file.write('  EPS_NETWORK_FEATURE_SUPPORT_IMS_VOICE_OVER_PS_SESSION_IN_S1      = "no";    # DO NOT CHANGE\n')
		mme_conf_file.write('  EPS_NETWORK_FEATURE_SUPPORT_EMERGENCY_BEARER_SERVICES_IN_S1_MODE = "no";    # DO NOT CHANGE\n')
		mme_conf_file.write('  EPS_NETWORK_FEATURE_SUPPORT_LOCATION_SERVICES_VIA_EPC            = "no";    # DO NOT CHANGE\n')
		mme_conf_file.write('  EPS_NETWORK_FEATURE_SUPPORT_EXTENDED_SERVICE_REQUEST             = "no";    # DO NOT CHANGE\n')
		mme_conf_file.write('  # Display statistics about whole system (expressed in seconds)\n')
		mme_conf_file.write('  MME_STATISTIC_TIMER = 10;\n')
		mme_conf_file.write('  # Amount of time in seconds the source MME waits to release resources after HANDOVER/TAU is complete (with or without.\n')
		mme_conf_file.write('  MME_MOBILITY_COMPLETION_TIMER = 1;\n')
		mme_conf_file.write('  # Amount of time in seconds the target MME waits to check if a handover/tau process has completed successfully.\n')
		mme_conf_file.write('  MME_S10_HANDOVER_COMPLETION_TIMER = 1;\n')
		mme_conf_file.write('  IP_CAPABILITY = "IPV4V6";\n')
		mme_conf_file.write('  INTERTASK_INTERFACE :\n')
		mme_conf_file.write('  {\n')
		mme_conf_file.write('    ITTI_QUEUE_SIZE = 2000000;\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  S6A :\n')
		mme_conf_file.write('  {\n')
		mme_conf_file.write('    S6A_CONF = "'+self.prefix+'/mme_fd.conf";\n')
		mme_conf_file.write('    HSS_HOSTNAME = "hss"; # THE HSS HOSTNAME (not HSS FQDN)\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  SCTP :\n')
		mme_conf_file.write('  {\n')
		mme_conf_file.write('    SCTP_INSTREAMS = 8;\n')
		mme_conf_file.write('    SCTP_OUTSTREAMS = 8;\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  S1AP : \n')
		mme_conf_file.write('  {')
		mme_conf_file.write('    S1AP_OUTCOME_TIMER = 10;\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  GUMMEI_LIST = (\n')
		mme_conf_file.write('    {MCC="'+self.mcc+'" ; MNC="'+self.mnc+
												'"; MME_GID="'+self.mme_gid+'" ; MME_CODE="'+
												self.mme_code+'";}\n')
		mme_conf_file.write('  );\n')
		mme_conf_file.write('  TAI_LIST = (\n')
		for tai in tais[ 0:len(tais)-1 ]:
			tai_elmnts = tai.split(' ')
			mme_conf_file.write('    {MCC="'+tai_elmnts[1]+'" ; MNC="'+tai_elmnts[2] + '";  TAC = "'+ tai_elmnts[0] +'"; },\n')
		tai = tais[len(tais) - 1]
		tai_elmnts = tai.split(' ')
		mme_conf_file.write('    {MCC="'+tai_elmnts[1]+'" ; MNC="' + tai_elmnts[2]+ '";  TAC = "' + tai_elmnts[0] +'"; }\n')
		mme_conf_file.write('  );\n')
		mme_conf_file.write('  NAS :\n')
		mme_conf_file.write('  {\n')
		mme_conf_file.write('    ORDERED_SUPPORTED_INTEGRITY_ALGORITHM_LIST = [ "EIA2" , "EIA1" , "EIA0" ];\n')
		mme_conf_file.write('    ORDERED_SUPPORTED_CIPHERING_ALGORITHM_LIST = [ "EEA0" , "EEA1" , "EEA2" ];\n')
		mme_conf_file.write('    T3402 =  12; # in minutes (default is 12 minutes)\n')
		mme_conf_file.write('    T3412 =  54; # in minutes (default is 54 minutes, network dependent)\n')
		mme_conf_file.write('    T3422 =  6;  # in seconds (default is 6s)\n')
		mme_conf_file.write('    T3450 =  6;  # in seconds (default is 6s)\n')
		mme_conf_file.write('    T3460 =  6;  # in seconds (default is 6s)\n')
		mme_conf_file.write('    T3470 =  6;  # in seconds (default is 6s)\n')
		mme_conf_file.write('    T3485 =  8;  # in seconds (default is 8s)\n')
		mme_conf_file.write('    T3486 =  8;  # UNUSED in seconds (default is 8s)\n')
		mme_conf_file.write('    T3489 =  4;  # in seconds (default is 4s)\n')
		mme_conf_file.write('    T3495 =  8;  # UNUSED in seconds (default is 8s)\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  NETWORK_INTERFACES : \n')
		mme_conf_file.write('  {\n')
		mme_conf_file.write('    # MME binded interface for S1-C or S1-MME  communication (S1AP), can be ethernet interface, virtual ethernet interface, we dont advise wireless interfaces\n')
		mme_conf_file.write('    MME_INTERFACE_NAME_FOR_S1_MME   = "' + self.mme_s1c_name+'"; # YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('    MME_IPV4_ADDRESS_FOR_S1_MME     = "' + self.mme_s1c_IP+'/24"; # CIDR, YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('    # MME binded interface for S11 communication (GTPV2-C)\n')
		mme_conf_file.write('    MME_INTERFACE_NAME_FOR_S11      = "' + self.mme_s11_name+'"; # YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('    MME_IPV4_ADDRESS_FOR_S11        = "' + str(self.mme_s11_IP)+'/24"; # CIDR, YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('    MME_PORT_FOR_S11                = 2123;# YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('    #S10 Interface\n')
		if useLoopBackForS10:
			mme_conf_file.write('    MME_INTERFACE_NAME_FOR_S10      = "lo"; # YOUR NETWORK CONFIG HERE\n')
			mme_conf_file.write('    MME_IPV4_ADDRESS_FOR_S10        = "127.0.0.10/24"; # CIDR, YOUR NETWORK CONFIG HERE\n')
		else:
			mme_conf_file.write('    MME_INTERFACE_NAME_FOR_S10      = "' + self.mme_s10_name+'"; # YOUR NETWORK CONFIG HERE\n')
			mme_conf_file.write('    MME_IPV4_ADDRESS_FOR_S10        = "' + str(self.mme_s10_IP)+'/24"; # CIDR, YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('    MME_PORT_FOR_S10                = 2123; # YOUR NETWORK CONFIG HERE\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  LOGGING :\n')
		mme_conf_file.write('  {\n')
		mme_conf_file.write('    # OUTPUT choice in { "CONSOLE", `path to file`", "`IPv4@`:`TCP port num`"}\n')
		mme_conf_file.write('    # `path to file` must start with . or /\n')
		mme_conf_file.write('    # if TCP stream choice, then you can easily dump the traffic on the remote or local host: nc -l `TCP port num` > received.txt\n')
		mme_conf_file.write('    OUTPUT            = "CONSOLE";\n')
		mme_conf_file.write('    THREAD_SAFE       = "no";  # THREAD_SAFE choice in { "yes", "no" }, safe to let no\n')
		mme_conf_file.write('    COLOR             = "yes"; # COLOR choice in { "yes", "no" } means use of ANSI styling codes or no\n')
		mme_conf_file.write('    # Log level choice in { "EMERGENCY", "ALERT", "CRITICAL", "ERROR", "WARNING", "NOTICE", "INFO", "DEBUG", "TRACE"}\n')
		mme_conf_file.write('    SCTP_LOG_LEVEL    = "TRACE";\n')
		mme_conf_file.write('    S11_LOG_LEVEL     = "TRACE";\n')
		mme_conf_file.write('    GTPV2C_LOG_LEVEL  = "TRACE";\n')
		mme_conf_file.write('    UDP_LOG_LEVEL     = "TRACE";\n')
		mme_conf_file.write('    S1AP_LOG_LEVEL    = "TRACE";\n')
		mme_conf_file.write('    NAS_LOG_LEVEL     = "TRACE";\n')
		mme_conf_file.write('    MME_APP_LOG_LEVEL = "TRACE";\n')
		mme_conf_file.write('    S6A_LOG_LEVEL     = "TRACE";\n')
		mme_conf_file.write('    UTIL_LOG_LEVEL    = "TRACE";\n')
		mme_conf_file.write('    MSC_LOG_LEVEL     = "ERROR";\n')
		mme_conf_file.write('    ITTI_LOG_LEVEL    = "ERROR";\n')
		mme_conf_file.write('    MME_SCENARIO_PLAYER_LOG_LEVEL = "TRACE";\n')
		mme_conf_file.write('    ASN1_VERBOSITY    = "annoying";\n')
		mme_conf_file.write('  };\n')
		mme_conf_file.write('  WRR_LIST_SELECTION = (\n')
		previous_tac = 0
		for tai in tais[ 0:len(tais)-1 ]:
			tai_elmnts = tai.split(' ')
			tac = int(tai_elmnts[0])
			if tac != previous_tac:
				tac_lb = tac % 256
				tac_hb = tac // 256
				mme_conf_file.write('    {ID="tac-lb' + str(format(tac_lb, '02x')) +
						'.tac-hb' + str(format(tac_hb, '02x')) +
						'.tac.epc.mnc' + self.mnc +
						'.mcc' + self.mcc +
						'.3gppnetwork.org" ; SGW_IP_ADDRESS_FOR_S11="' +
						str(self.spgwc0_s11_IP) + '";},\n')
				previous_tac = tac
		tai = tais[len(tais) - 1]
		tai_elmnts = tai.split(' ')
		tac = int(tai_elmnts[0])
		tac_lb = tac % 256
		tac_hb = tac // 256
		mme_conf_file.write('    {ID="tac-lb' + str(format(tac_lb, '02x')) +
						'.tac-hb' + str(format(tac_hb, '02x')) +
						'.tac.epc.mnc' + self.mnc +
						'.mcc' + self.mcc +
						'.3gppnetwork.org" ; SGW_IP_ADDRESS_FOR_S11="' +
						str(self.spgwc0_s11_IP) +'";}\n')
		mme_conf_file.write('  );\n')
		mme_conf_file.write('};\n')
		mme_conf_file.close()

		mmeFile = open('./mme-cfg.sh', 'w')
		mmeFile.write('#!/bin/bash\n')
		mmeFile.write('\n')
		mmeFile.write('set -x\n')
		if self.fromDockerFile:
			mmeFile.write('cd /openair-mme/scripts\n')
		else:
			mmeFile.write('cd /root/openair-mme/scripts\n')
		mmeFile.write('\n')
		mmeFile.write('INSTANCE=1\n')
		mmeFile.write('PREFIX=\''+self.prefix+'\'\n')
		# The following variables could be later be passed as parameters
		mmeFile.write('MY_REALM=\''+self.realm+'\'\n')
		mmeFile.write('\n')
		if not self.fromDockerFile:
			mmeFile.write('rm -Rf $PREFIX\n')
			mmeFile.write('\n')
			mmeFile.write('mkdir -p $PREFIX\n')
			mmeFile.write('\n')
			mmeFile.write('cp ../etc/mme_fd.sprint.conf $PREFIX/mme_fd.conf\n')
			mmeFile.write('\n')
		mmeFile.write('declare -A MME_CONF\n')
		mmeFile.write('\n')
		mmeFile.write('pushd $PREFIX\n')
		mmeFile.write('MME_CONF[@MME_S6A_IP_ADDR@]="' + self.mme_s6a_IP + '"\n')
		mmeFile.write('MME_CONF[@INSTANCE@]=$INSTANCE\n')
		mmeFile.write('MME_CONF[@PREFIX@]=$PREFIX\n')
		mmeFile.write('MME_CONF[@REALM@]=$MY_REALM\n')
		mmeFile.write('MME_CONF[@MME_FQDN@]="mme.${MME_CONF[@REALM@]}"\n')
		mmeFile.write('MME_CONF[@HSS_HOSTNAME@]=\'hss\'\n')
		mmeFile.write('MME_CONF[@HSS_FQDN@]="${MME_CONF[@HSS_HOSTNAME@]}.${MME_CONF[@REALM@]}"\n')
		mmeFile.write('MME_CONF[@HSS_IP_ADDR@]="' + self.hss_s6a_IP + '"\n')
		mmeFile.write('\n')
		mmeFile.write('for K in "${!MME_CONF[@]}"; do \n')
		mmeFile.write('  egrep -lRZ "$K" $PREFIX | xargs -0 -l sed -i -e "s|$K|${MME_CONF[$K]}|g"\n')
		mmeFile.write('  ret=$?;[[ ret -ne 0 ]] && echo "Tried to replace $K with ${MME_CONF[$K]}"\n')
		mmeFile.write('done\n')
		mmeFile.write('\n')
		if not self.fromDockerFile:
			mmeFile.write('sed -i -e \'s/'+self.mme_s6a_IP+'.*$/'+self.mme_s6a_IP+ '\ mme\ /g\' /etc/hosts\n')
		mmeFile.write('# Generate freeDiameter certificate\n')
		mmeFile.write('popd\n')
		mmeFile.write('./check_mme_s6a_certificate $PREFIX mme.${MME_CONF[@REALM@]}\n')
		mmeFile.write('set +x\n')
		mmeFile.close()

#-----------------------------------------------------------
# Usage()
#-----------------------------------------------------------
def Usage():
	print('--------------------------------------------------------------------')
	print('generate_mme_config_script.py')
	print('   Prepare a bash script to be run in the workspace where MME is ')
	print('   being built.')
	print('   That bash script will copy configuration template files and adapt')
	print('   to your configuration.')
	print('--------------------------------------------------------------------')
	print('Usage: python3 generate_mme_config_script.py [options]')
	print('  --help  Show this help.')
	print('-------------------------------------------------- HSS Options -----')
	print('  --kind=MME')
	print('  --hss_s6a=[HSS S6A Interface IP server]')
	print('  --mme_s6a=[MME S6A Interface IP server]')
	print('  --mme_s1c_IP=[MME S1-C Interface IP address]')
	print('  --mme_s1c_name=[MME S1-C Interface name]')
	print('  --mme_s10_IP=[MME S10 Interface IP address]')
	print('  --mme_s10_name=[MME S10 Interface name]')
	print('  --mme_s11_IP=[MME S11 Interface IP address]')
	print('  --mme_s11_name=[MME S11 Interface name]')
	print('  --spgwc0_s11_IP=[SPGW-C Instance 0 - S11 Interface IP address]')
	print('  --mme_gid=[MME Group ID for GUMMEI]')
	print('  --mme_code=[MME code for GUMMEI]')
	print('  --mcc=[MCC for GUMMEI]')
	print('  --mnc=[MNC for GUMMEI]')
	print('  --tai_list=["TAIs"]')
	print('  --realm=["REALM"]')
	print('  --prefix=["Prefix for configuration files"]')
	print('  --from_docker_file')

argvs = sys.argv
argc = len(argvs)
cwd = os.getcwd()

myMME = mmeConfigGen()

while len(argvs) > 1:
	myArgv = argvs.pop(1)
	if re.match('^\-\-help$', myArgv, re.IGNORECASE):
		Usage()
		sys.exit(0)
	elif re.match('^\-\-kind=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-kind=(.+)$', myArgv, re.IGNORECASE)
		myMME.kind = matchReg.group(1)
	elif re.match('^\-\-hss_s6a=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-hss_s6a=(.+)$', myArgv, re.IGNORECASE)
		myMME.hss_s6a_IP = matchReg.group(1)
	elif re.match('^\-\-mme_s6a=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s6a=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s6a_IP = matchReg.group(1)
	elif re.match('^\-\-mme_s1c_IP=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s1c_IP=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s1c_IP = matchReg.group(1)
	elif re.match('^\-\-mme_s1c_name=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s1c_name=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s1c_name = matchReg.group(1)
	elif re.match('^\-\-mme_s10_IP=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s10_IP=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s10_IP = ipaddress.ip_address(matchReg.group(1))
	elif re.match('^\-\-mme_s10_name=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s10_name=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s10_name = matchReg.group(1)
	elif re.match('^\-\-mme_s11_IP=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s11_IP=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s11_IP = ipaddress.ip_address(matchReg.group(1))
	elif re.match('^\-\-mme_s11_name=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_s11_name=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_s11_name = matchReg.group(1)
	elif re.match('^\-\-spgwc0_s11_IP=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-spgwc0_s11_IP=(.+)$', myArgv, re.IGNORECASE)
		myMME.spgwc0_s11_IP = ipaddress.ip_address(matchReg.group(1))
	elif re.match('^\-\-mme_gid=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_gid=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_gid = matchReg.group(1)
	elif re.match('^\-\-mme_code=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mme_code=(.+)$', myArgv, re.IGNORECASE)
		myMME.mme_code = matchReg.group(1)
	elif re.match('^\-\-mcc=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mcc=(.+)$', myArgv, re.IGNORECASE)
		myMME.mcc = matchReg.group(1)
	elif re.match('^\-\-mnc=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-mnc=(.+)$', myArgv, re.IGNORECASE)
		myMME.mnc = matchReg.group(1)
	elif re.match('^\-\-tai_list=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-tai_list=(.+)$', myArgv, re.IGNORECASE)
		myMME.tai_list = str(matchReg.group(1))
	elif re.match('^\-\-realm=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-realm=(.+)$', myArgv, re.IGNORECASE)
		myMME.realm = matchReg.group(1)
	elif re.match('^\-\-prefix=(.+)$', myArgv, re.IGNORECASE):
		matchReg = re.match('^\-\-prefix=(.+)$', myArgv, re.IGNORECASE)
		myMME.prefix = matchReg.group(1)
	elif re.match('^\-\-from_docker_file', myArgv, re.IGNORECASE):
		myMME.fromDockerFile = True
	else:
		Usage()
		sys.exit('Invalid Parameter: ' + myArgv)

print(myMME.spgwc0_s11_IP)
if myMME.kind == '':
	Usage()
	sys.exit('missing kind parameter')

if myMME.kind == 'MME':
	if myMME.mme_s6a_IP == '':
		Usage()
		sys.exit('missing MME S6A IP address')
	elif myMME.hss_s6a_IP == '':
		Usage()
		sys.exit('missing HSS S6A IP address')
	elif myMME.mme_s1c_IP == '':
		Usage()
		sys.exit('missing MME S1-C IP address')
	elif myMME.mme_s1c_name == '':
		Usage()
		sys.exit('missing MME S1-C Interface name')
	elif myMME.mme_s10_IP == '':
		Usage()
		sys.exit('missing MME S10 IP address')
	elif myMME.mme_s10_name == '':
		Usage()
		sys.exit('missing MME S10 Interface name')
	elif myMME.mme_s11_IP == '':
		Usage()
		sys.exit('missing MME S11 IP address')
	elif myMME.mme_s11_name == '':
		Usage()
		sys.exit('missing MME S11 Interface name')
	elif myMME.spgwc0_s11_IP == '':
		Usage()
		sys.exit('missing SPGW-C0 IP address')
	elif myMME.mme_gid == '':
		Usage()
		sys.exit('missing mme_gid')
	elif myMME.mme_code == '':
		Usage()
		sys.exit('missing mme_code')
	elif myMME.mcc == '':
		Usage()
		sys.exit('missing mcc')
	elif myMME.mnc == '':
		Usage()
		sys.exit('missing mnc')
	elif myMME.tai_list == '':
		Usage()
		sys.exit('missing tai_list')
	elif myMME.realm == '':
		Usage()
		sys.exit('missing realm')
	elif myMME.prefix == '':
		Usage()
		sys.exit('missing prefix')
	else:
		myMME.GenerateMMEConfigurer()
		sys.exit(0)
else:
	Usage()
	sys.exit('unsupported kind parameter')
