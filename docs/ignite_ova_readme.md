#####1. Ignite VM access details
     user/pwd: ignite/ignite

#####2. Update Ignite server config file 
     Change directory to /var/www/
     Edit Ignite/ignite/ignite/config.py and update IGNITE_IP to the IP address on which to host Ignite server

#####3. Run python Ignite/ignite/setup.py with sudo privilege.   
   Answer on prompt as following:

     Have you modified Ignite settings in ignite/conf.py? [y/n]    y
     
     Install system dependencies? [y/n]      n
       
     Install python dependencies? [y/n]      n  

#####4. Restart the apache2 server 
     sudo service apache2 restart 
 
#####5. Access Ignite server UI
   Type following on web browser:

     http://<IGNITE_IP:8000>/ui/index.html#/

   Where IGNITE_IP is the IP address that has been configured in conf.py in step 2
 
   Ignite UI access details:

     user/pwd: admin/admin   