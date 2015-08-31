Getting started with Ignite:


Option 1: Download OVA from link below:
https://cisco.box.com/shared/static/7om0zdujm98e0u9g7kpbergau0znphq4.ova
Follow steps 4-7 below (skip step 6)


Option 2: Create a new Ignite VM/Server with code from git 
1. Install postgresql
# apt-get install postgresql-9.3 postgresql-common  

2. Set up database
# psql  –U postgres
# create database  DATABASE_NAME;
Disconnect from psql.
 
2. Update server settings
Edit  following section in ~ignite/ignite/ignite/prod.py
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

3. Create tables in database
# python ~ignite/ignite/ignite/manage.py makemigrations
# python ~ignite/ignite/ignite/manage.py migrate

4. Edit following line ~ignite/ignite/ignite/dist/scripts/utils/settings.*.js to ignite server ip and port. 
"baseURL" : "http://localhost:9010"

5.Run server
# python manage.py runserver <ip:port>

6. Run following command to create user on server
# curl -X POST -i -H "Content-type: application/json" http://ip:port/auth/register/  -d '{"username”:”admin”, "password”:”admin”, "email":"username@xyz.com"}'

7. Run UI on web browser
http://ip:port/ui/index.html#/
Login using credentials: admin/admin
