
import os
from fabric.api import run,local,env 
from fabric.contrib import files
from fabric.operations import sudo
import boto
from boto.ec2.connection import EC2Connection
from boto.ec2 import *
import time

dwndir = '/home/%s/installs' % env.user
env.user = 'ec2-user'
#env.hosts = 'pub_dns'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
key_pair = ''

ec2_conn = EC2Connection('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY')

def CreateInstance():
	"""
	Used to Create New Instance 
	"""
	reservation = ec2_conn.run_instances('ami-31814f58', min_count='1', 
						    max_count='1', key_name='My-Key-Pair',
						    instance_type='t1.micro')
	instance = reservation.instances[0]
	print "Waiting for Instance to start ...."
	status = instance.update()
	while status != "running":
 		status = instance.update()
		print status
		time.sleep(25)
		env.hosts = instance.public_dns_name
		print env.hosts

def DownloadNagios():
	"""
	Used to Download Nagios
	"""
	MKDIR_CMD = "mkdir /home/%s/installs" % env.user
	run(MKDIR_CMD)
	DWNNAGIOS_CMD = "wget -P %s http://sourceforge.net/projects/nagios/files/nagios-3.x/nagios-3.3.1/nagios-3.3.1.tar.gz/download" % (dwndir)
	run(DWNNAGIOS_CMD)

def UbuntuDependencyInstall():
	sudo("apt-get install build-essential")
	sudo("apt-get install php")
	sudo("apt-get install gd gd-devel")
	sudo("apt-get install apache2")
	sudo("apt-get install xinetd")
	sudo("apt-get install openssl libssl-dev libcurl3-openssl-dev")

def NonUbuntuDependencyInstall():
	sudo("yum groupinstall -y 'Development Tools'")
	sudo("yum install -y php")
	sudo("yum install -y gd")
	sudo("yum install -y gd-devel")
	sudo("yum install -y httpd")
	sudo("yum install -y gcc glibc glibc-common")
	sudo("yum install -y gcc glibc glibc-common")
	sudo("yum install -y xinetd")
	sudo("yum install -y openssl openssl-devel")

def DependencyInstall():
	"""
	Used to install Dependencies
	"""
	os = run("uname -a | cut -d' ' -f4 | cut -c 5-10")
	if os == "Ubuntu":
		UbuntuDependencyInstall()
	else:
		NonUbuntuDependencyInstall()

def ExtractNagios():
	"""
	Used TO Extract Nagios Downloaded Package
	"""
	TAR_CMD = "cd %s && tar -zxvf nagios-3.3.1.tar.gz" % (dwndir)
	run(TAR_CMD)

def Createuser():
	"""
	Used to Create Nagios User, Group & Adding Nagios User & Apache USer to Nagios Group
	"""
	sudo("useradd -m nagios")
	sudo("groupadd nagcmd")
	sudo("usermod -a -G nagcmd nagios")
	sudo("usermod -a -G nagcmd apache")

def RunConfigScript():
	"""
	Used to Run Nagios Configure Script
	"""
	CONF_CMD = "cd %s/nagios && ./configure --with-command-group=nagcmd" % (dwndir)
	sudo(CONF_CMD)

def CompileSource():
	"""
	Used to Compile Nagios Source Code
	"""
	COMP_CMD = "cd %s/nagios && make all" % (dwndir)
	sudo(COMP_CMD)

def InstallSource():
	"""
	Used to Install Compiled Source Code
	"""
	INST_CMD = "cd %s/nagios && make install" % (dwndir)
	sudo(INST_CMD)
	INIT_CMD = "cd %s/nagios && make install-init" % (dwndir)
	sudo(INIT_CMD)
	INST_CONF_CMD = "cd %s/nagios && make install-config" % (dwndir)
	sudo(INST_CONF_CMD)
	INST_CMD_MODE = "cd %s/nagios && make install-commandmode" % (dwndir)
	sudo(INST_CMD_MODE)
	INST_WEB_CMD = "cd %s/nagios && make install-webconf" % (dwndir)
	sudo(INST_WEB_CMD)
	CRT_USR_CMD = "cd %s/nagios && htpasswd -c /usr/local/nagios/etc/htpasswd.users nagiosadmin" % (dwndir)
	sudo(CRT_USR_CMD)
	
def ApacheRestart():
	"""
	Used to Restart Apache Server
	"""
	sudo("/etc/init.d/httpd restart")

def NagiosPluginDownload():
	"""
	Used to Download Nagios Plugin
	"""
	DWNPLUGIN_CMD = "wget -P %s http://sourceforge.net/projects/nagiosplug/files/nagiosplug/1.4.15/nagios-plugins-1.4.15.tar.gz/download" % (dwndir)
	run(DWNPLUGIN_CMD)
	TAR_PLG_CMD = "cd %s && tar -zxvf nagios-plugins-1.4.15.tar.gz" % (dwndir)
	run(TAR_PLG_CMD)

def PluginConfig():
	"""
	Used to Run Plugin Configure Script
	"""
	PLG_CONF_CMD = "cd %s/nagios-plugins-1.4.15 && ./configure --with-nagios-user=nagios --with-nagios-group=nagios" % (dwndir)
	run(PLG_CONF_CMD)
	
def InstallPlugin():
	"""
	Used to Install Nagios Plugin
	"""
	PLG_COMP_CMD = "cd %s/nagios-plugins-1.4.15 && make" % (dwndir)
	sudo(PLG_COMP_CMD)
	PLG_INST_CMD = "cd %s/nagios-plugins-1.4.15 && make install" % (dwndir)
	sudo(PLG_INST_CMD)

def NagiosServiceAdd():
	"""
	Used to Add Nagios Service in System Startup
	"""
	SRVC_ADD_CMD = "chkconfig --add nagios && chkconfig nagios on"
	sudo(SRVC_ADD_CMD)

def NagiosVerify():
	"""
	Used to Verify Nagios Sample Config Files
	"""
	NGS_VRF_CMD = "/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg"
	sudo(NGS_VRF_CMD)

def NagiosRestart():
	"""
	Used to Restart Nagios Service
	"""
	NGS_RST_CMD = "/etc/init.d/nagios restart"
	sudo(NGS_RST_CMD)

def NagiosFullInstall():
	"""
	Used to Install Full Nagios
	"""
	DependencyInstall()
	DownloadNagios()
	ExtractNagios()		
	Createuser()
	RunConfigScript()
	CompileSource()
	InstallSource()
	ApacheRestart()

def NagiosPluginFullInstall():
	"""
	Used to Install Full Nagios Plugin
	"""
	NagiosPluginDownload()
	PluginConfig()
	InstallPlugin()
	NagiosServiceAdd()
	NagiosVerify()
	NagiosRestart()

def Nagiosnrpe():
	"""
	Used to Download Nagios NRPE Client
	"""
	NRPE_DWNL_CMD = "wget -P %s http://nchc.dl.sourceforge.net/project/nagios/nrpe-2.x/nrpe-2.13/nrpe-2.13.tar.gz" % (dwndir)
	run(NRPE_DWNL_CMD)
	NRPE_EXT_CMD = "cd %s && tar -zxvf nrpe-2.13.tar.gz" % (dwndir)

def NrpeSetup():
	"""
	Used to Configure & Install NRPE Client NOTE: Before Running this command make sure openssl & openssl-devel packages are installed
	"""
	NRPE_CONF_CMD = "cd %s/nrpe-2.13 && ./configure" % (dwndir)
	run(NRPE_CONF_CMD)
	NRPE_MAKE_CMD = "cd %s && make all" % (dwndir)
	sudo(NRPE_MAKE_CMD)
	NRPE_PLG_CMD = "cd %s && make install-plugin" % (dwndir)
	sudo(NRPE_PLG_CMD)
	NRPE_DMN_CMD = "cd %s && make install-daemon" % (dwndir)
	sudo(NRPE_DMN_CMD)
	NRPE_DMNCONF_CMD = "cd %s && make install-daemon-config" % (dwndir)
	sudo(NRPE_DMNCONF_CMD)
	NRPE_XINETD_CMD = "cd %s && make install-xinetd" % (dwndir)
	sudo(NRPE_XINETD_CMD)
	NRPE_SRVC_CMD = "echo 'nrpe               5666/tcp                                  # NRPE' >> /etc/services"
	sudo(NRPE_SRVC_CMD)
	NRPE_STRT_CMD = "/etc/init.d/xinetd restart"
	sudo(NRPE_STRT_CMD)

def NrpeRestart():
	"""
	Used to Restart NRPE Service
	"""
	NRPE_STRT_CMD = "/etc/init.d/xinetd restart"
	sudo(NRPE_STRT_CMD)

def NrpeFullInstall():
	"""
	Used to Install NRPE NOTE: Before Running this command make sure openssl & openssl-devel packages are installed
	"""
	Nagiosnrpe()
	NrpeSetup()
	
	

