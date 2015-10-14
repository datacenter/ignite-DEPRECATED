![Ignite](https://github.com/datacenter/ignite/blob/master/dist/images/color-logo.png)

# Description

Ignite is a tool to bootstrap your network. It supports Cisco Nexus switches leveraging Power-On Auto Provisioning (POAP) capabilities.

Ignite provides bootstrapping with the following capabilities:
* Topology design
* Configuration design
* Image and configuration store for POAP
* POAP request handler

![Ignite Screenshot](https://github.com/datacenter/ignite/blob/master/dist/images/ignite-screenshot.png)

# Getting Started

### Option 1: Download OVA from link below:
https://cisco.box.com/s/4mdfja1cbev3065vmwst4fvc7nj9vpe2

Username/password: ignite/ignite

Follow steps 4-7 below (skip step 6)

	a. Deploy OVA
	b. Login with ignite/ignite
	c. Change directory to ~/ignite/ignite (cd ~/ignite/ignite)
	d. Change to sudo (sudo su)
	e. Edit configure.sh to edit parameter values of following parameters
	   	ignite_ip :  IP address on which to run the server
	    ignite_port: port on which to run the server
	    vmusername: username for the server
	    vmpassword: password for the server
	f. Run configure.sh (sh configure.sh)
	g. Run ignite server (python manage.py runserver ip:port ) where IP is the address provided in ignite_ip and port is value provided in ignite_port.
	h. To launch UI use http://<ipaddress>:<port>/ui/index.html
	i. Use New User registration link in the UI to create a new user credential. Login to the page using this credential.

Setup users as mentioned in step-6 below.

### Option 2: Create a new Ignite VM/Server with code from git

1.Install postgresql
```
apt-get install postgresql-9.3 postgresql-common
```

2.Set up database
```
psql  –U postgres
create database  DATABASE_NAME;
\q
```

Edit  following section in ~/ignite/ignite/prod.py
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ‘DATABASE_NAME’,                  #Name of database created
        'USER': 'postgres',                       #Database User
        'PASSWORD': 'PASSWORD',                   #password for Database user
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}
```

3.Create tables in database
```
python ~ignite/ignite/manage.py makemigrations
python ~ignite/ignite/manage.py migrate
```

4.Edit following line ~ignite/ignite/dist/scripts/utils/settings.*.js to ignite server ip and port (8000).
```
"baseURL" : "http://localhost:9010"
```
to
```
"baseURL" : "http://<ignite_vm_ip>:<port>"

```

5.Run server
```
python manage.py runserver <ip:port>
```

6.Run following command to create user on server
```
curl -X POST -i -H "Content-type: application/json" http://<ignite_vm_ip>:<port>/auth/register/  -d '{"username”:”admin”, "password”:”admin”, "email":"username@xyz.com"}'
```

7.Run UI on web browser
  To launch UI use http://<ipaddress>:<port>/ui/index.html
  Use New User registration link in the UI to create a new user credential. Login to the page using this credential.

### Installing poap.py in the script server
```
1.Ignite_poap.py – sample poap.py script is available in github

```
2.Modify ignite_poap.py to assign ip address and port number of the ignite server (see the ip address and port number used while executing manage.py run server)
```
	a. Search for “ignite server” in poap.py and change the following values
		#ignite server
		hostname = "172.31.219.76"
		port = "8001"
	b. Save the changes
	c. Copy and rename the file to “poap.py” in the script server directory /var/lib/tftpboot
```
3.Please note, poap.py should be installed in the script server whose address is returned in the DHCP OFFER during the dhcp discover process
```
# License

Copyright 2015 Cisco Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
