#!/bin/sh


#------------Configureable parameters-------------
#Ignite server IP and Port
IGNITE_IP='127.0.0.1'
IGNITE_PORT='8000'

#Ignite server access details
VMUSERNAME='ignite'
VMPASSWORD='ignite'

#Database Parameters
DBNAME='ignitedb'
DBUSER='postgres'
DBPASSWORD='password'
DBHOST='localhost'
DBPORT=''

#Server Directory
#If hosted using Apache2
#Set it to path relative to apache2 directory if hosted using apache2
#Example: if manage.py is located inside /var/www/ignite/ignite PROJECT_DIR should be as following
#PROJECT_DIR = '/ignite/ignite/'
#Example: if manage.py is located inside /home/linux-user/workspace/ignite/ignite PROJECT_DIR should be as following
#PROJECT_DIR = '../../home/linux-user/workspace/ignite/ignite/'

#If not hosted using Apache2
PROJECT_DIR = '/'

#Server Configuration Repo Directory
#Base directory will be PROJECT_DIR
REPO = '/repo/'

#--------------------------------------------------

# location of syslog file if not in /var/log/syslog
REMOTE_SYSLOG_PATH = '/var/log/remote/ignite/system-'
# default switch image name
DEFAULT_SWITCH_IMAGE_NAME = 'n9000-dk9.6.1.2.I3.2.bin'
