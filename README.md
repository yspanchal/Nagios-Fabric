Nagios-Fabric
=============

Nagios-Fabric Script

	This is Nagios Fabric Script for installation of NAGIOS, NAGIOS_PLUGIN & NRPE. This script can be used to deploy Nagios on EC2 using EC2 Python BOTO package.

Usage :

install python fabric & boto

using easy install:

	easy_install fabric

	easy_install boto

using python-pip:

	pip install fabric
	
	pip install boto

git clone https://github.com/yspanchal/Nagios-Fabric.git

cd Nagios-Fabric/

fab -l

(1) To create EC2 Instance Using This Script use command (To create Instance provide AWS Access Key, AWS Secret Key, AMI ID For Ex:ami-31814f58, instance_type, & Key Pair )

fab CreateInstance

	This Command will create EC2 instance. & if you want to install Nagios Server on this instance use following command

fab NagiosFullInstall

fab NagiosPluginFullInstall

fab NrpeFullInstall

After Installation point your browser to http://IP-ADDRESS/nagios

 
