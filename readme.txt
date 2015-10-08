1. Install python dependencies
#pip install -r requirement.txt

2. Install postgresql
#apt-get install postgresql-9.3 postgresql-common

3. Set up database
#psql  –U postgres
#create database  DATABASE_NAME;
Disconnect from psql.

In case of authentication issues in postgres please refer following docs.

3.a. How to setup password for postgres user ? 
http://www.postgresql.org/message-id/4D958A35.8030501@hogranch.com

3.b. Various postgres authentication methods ?
http://www.postgresql.org/docs/9.1/static/auth-methods.html


4. Update server settings
#cd ~poap_server/ignite/ignite/


4.a. Edit  following section in prod.py
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


4.b. In prod.py set
UI_ROOT to '~ignite/ignite/dist'


5. Update UI server setting to point to ignite server ip:port
#cd  ~ignite/ignite/dist/scripts/utils


5.a. Edit folllowing section
    "appAPI": {
        "baseURL": "http://127.0.0.1:8888",     #configure ignite server ip:port
        "configlets" : {
       

6. Create tables in database
#cd ~/ignite/ignite/
#python manage.py makemigrations
#python manage.py migrate


7.Run server
#python manage.py runserver <ip:port>


8. Run following command to create user on server on a different server
#curl -X POST -i -H "Content-type: application/json" http://ip:port/auth/register/  -d '{"username":"username", "password":"pwd", "email":"username@xyz.com"}'


9. Run UI on web browser
http://ip:port/ui/index.html#/
Login using username and password used in step 5.


10. Stop the server
To stop the srver kill the server process


11. Server logs 
Ignite server logs are stored in file ignite.log at ~ignite/ignite/.
