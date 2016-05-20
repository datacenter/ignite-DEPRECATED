#Ignite server installation guide
This guide contains the information about package requirements of and installation instructions for ignite server on Ubuntu server distribution 14.04.03 LTS.

  
##1. Prerequisite
Prerequisites can be installed either by separately installing each package as described further in this section or by using ignite setup script as described in section 4. 

###1.1. System package dependencies
- Python 2.7

        apt-get install python2.7 python-dev libpq-dev 
- Python pip

        apt-get install python-pip
- Postgresql 9.3

        apt-get install postgresql-9.3 postgresql-common
- RabbitMQ

        apt-get install rabbitmq-server

- Apache2

        apt-get install apache2 libapache2-mod-wsgi

###1.2. Python package dependencies

- django version 1.7.0

         pip install django==1.7.0
- djangorestframework version 3.1.1

         pip install djangorestframework==3.1.1
- djoser version 0.3.0

         pip install djoser==0.3.0
- psycopg2 version 2.6

         pip install psycopg2==2.6 
- netaddr version 0.7.10

         pip install netaddr==0.7.10
- pytz version 2015.4

         pip install pytz==2015.4
- pythondateutil version 2.4.2

         pip install pythondateutil==2.4.2 


##2. Ignite server integration with Apache2
Configure Apache2 to host Ignite server. By creating a virtual host which will listen on a port dedicated to Ignite server it's traffic can be segregated ignite from other web services.

###2.1. Apache2 configuration
       
####2.1.2. Port configuration (Assuming Ignite server is hosted on port 8000)
Add following statement to /etc/apache2/ports.conf

         Listen 8000
  
####2.1.3. Virtual host setup
Create file ignite.conf in direcotry /etc/apache2/sites-available/ and add following statements to it.

         <VirtualHost *:8000>

         <Directory /var/www/ignite/ignite >
         <Files wsgi.py>
             Require all granted
         </Files>
         </Directory>

         WSGIDaemonProcess ignite python-path=/var/www/ignite:/usr/local/lib/python2.7/dist-packages
         WSGIProcessGroup ignite
         WSGIScriptAlias / /var/www/ignite/ignite/wsgi.py

         WSGIPassAuthorization On
         DocumentRoot /var/www/ignite

         ErrorLog ${APACHE_LOG_DIR}/ignite_error.log
         CustomLog ${APACHE_LOG_DIR}/access.log combined

         LogLevel info

         </VirtualHost>

####2.1.4. Enabling the new site.
To enable the ignite.conf created in step 2.1.3. use a2ensite command.

         a2ensite /etc/apache2/sites-available/ignite.conf

####2.1.5. Restarting apache2 server

         service apache2 restart
     
##3. Ignite server installation
Clone in directory /var/www/ using github repository use **git clone** command.

         git clone <repo-url> --branch <branch-name>

###3.1. Update Ignite configuration parameters

  Edit ~ignite/ignite/conf.py file to update parameters.

  Parameter details-

######Database Parameters
        DB_NAME - Name of databse for the ignite server.
        DB_USER - Database user name for ignite server.
        DB_PASSWORD - Password for DB_USER.
        DB_HOST - IP address on which postgresql is listening(typically 127.0.0.1).
        DB_PORT - Port on which postgresql is listening(leave blank if postgres server is running on default port)
 
######Ignite server access details
        IGNITE_IP - IP address of VM on which ignite server will be hosted.
        IGNITE_PORT - Port on which Ignite server will listen.
        IGNITE_USER - User name for VM.
        IGNITE_PASSWORD - Password for VM.

######Log file path for switch specific logs file in Ignite server
**Note:** for generating log file for each switch individually see section 7.2
 
        REMOTE_SYSLOG_PATH - Path to switch specific log files along with file name prefix.

######Log file name, for RHEL, it is messages

        SYSLOG_PATH - File name of syslog/messages file with full path.

######syslog port
        SYSLOG_PORT - Port on which syslog server is listening(default is 514).

######ACCESS_METHODS
        ACCESS_PROTOCOL - Protocol for communication between Ignite server and switch during POAP. These options are supported : scp, http, tftp, sftp

######Number of lines to display in logs
        LOG_LINE_COUNT - POAP Logs for a switch can be accessed through Ignite UI. This parameter sets the limit on logs to be displayed in the UI.

######RabbitMQ Settings
**Note** Leave these parameter to default if there are no specific requirements.

        RMQ_USERNAME - Username for RMQ server.
        RMQ_PASSWORD - Password for RMQ_USERNAME.
        RMQ_VHOST - RMQ vhost.

######Celery Daemon Settings
**Note** Leave these parameter to default if there are no specific requirements.

        CELERYD_USER - Username for celery.
        CELERYD_GROUP - Password for CELERYD_USER.


  **Note:** Set parameter PROJECT_DIR to "ignite" if server is to be hosted using apache2. 

###3.2. Execute setup script
Installation script runs in three stages. It first installs system packages then python packages and the sets up the Ignite server. User can skip first 2 stages of installation during execution of setup script if dependencies had been installed beforehand. 

Run setup.py from /var/www/ directory with sudo privilege if server is hosted using apache2.

        sudo python ignite/setup.py

Sample output of a trial run of setup.py

       Have you modified Ignite settings in ignite/conf.py? [y/n] y

       Install system dependencies? [y/n] y

       Install Python 2.7 (may take a while) - [OK]
       Install Python dev (may take a while) - [OK]
       ...
       ...
       ...

       Install python dependencies? [y/n] y
       Install Python Packages (may take a while) - [OK]

       Setting up Ignite server
       Create Database (ignore error if database already exists) - [OK]
       Database Migrate - [OK]
       Load user fixture - [OK]
       Load image profile fixture - [OK]
       Load workflow fixtures - [OK]
       Javascript IP+Port Setting - [OK]
       POAP User Setting - [OK]
       POAP Password Setting - [OK]
       POAP IP Setting - [OK]
       POAP Port Setting - [OK]
       Bootstrap Config Syslog IP Setting - [OK]
       ...
       ...
       ...
              
###3.3. Load sample switch, line card and module data
To load server with sample switches, line cards and modules data change directory ~ignite/scripts/ and execute **switch_model_script.py** script.

       python switch_model_script.py

###3.4. Load sample feature JSONs
To load server with sample feature JSONs change directory ~ignite/scripts/ and execute **feature_script.py** script.

       python feature_script.py


##4. Run Ignite server
**Note**: If the server is hosted using apache2 please skip this step.

To run Ignite server change directory to ~/ignite. Execute following command with sudo privilege. Where **IGNITE\_IP** and **IGNITE\_PORT** are the server ip and port as has been set in ~ignite/ignite/conf.py

       sudo python manage.py runserver <IGNITE_IP>:<IGNITE_PORT>



##5. Access Ignite server
Web URL to access Ignite server
  
        http://<IGNITE_IP>:<IGNITE_PORT>/ui/index.html#/

Use user/password- **admin/admin** to login.


##6. Setup POAP script
POAP script- **poap.py**, is kept inside ~/ignite/scripts/ directory. Place his script in the TFTP server whose IP address is returned in DHCP response along with other parameters. 



##7. Remote syslog facility
POAP logs are logged by Ignite server using remote syslog facility.

###7.1. Enable remote syslog facility
Edit /etc/rsyslog.conf to add following lines

         $ModLoad imudp
         $UDPServerRun 514

Execute following command to estart rsyslog daemon

         service rsyslog restart 

###7.2. Create switch specific log files
To create switch specific log files add following lines to /etc/rsyslog.con

         $template DynaFile,"/var/log/remote/ignite/system-%HOSTNAME%.log"
         *.* -?DynaFile

Restart syslog server after saving the file.

For instance, for a switch with serial number SAL123 log will be stored in **/var/log/remote/ignite/** directory by the name **system-SAL123.log** 
