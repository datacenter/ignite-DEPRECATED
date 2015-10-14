#!/bin/sh


#------------Configureable parameters-------------
ignite_ip=127.0.0.1
ignite_port=8000

vmusername=ignite
vmpassword=ignite

dbname=ignitedb
dbuser=postgres
dbpassword=password
#--------------------------------------------------



#------------Script to modify the server settings--

path1=`pwd`
path2='dist/scripts/utils'
setting_filepath="$path1/$path2"
filename=`find "$setting_filepath" -name "setting*"`
sed -i 's/\(\"baseURL\"\s*\:\s*\"http\:\/\/\)\(.*\)\(\"\,\)/\1'"$ignite_ip"':'"$ignite_port"'\3/' "$filename"

path2='ignite/ignite.py'
filename="$path1/$path2"
sed -i  's/\(result\[\"config_username\"\]\s*=\s*\"\)\([A-Z a-z][0-9 A-Z a-z \! \@ \# \$]*\)\(\"\)/\1'"$vmusername"'\3/' "$filename"
sed -i  's/\(result\[\"config_password\"\]\s*=\s*\"\)\([A-Z a-z][0-9 A-Z a-z \! \@ \# \$]*\)\(\"\)/\1'"$vmpassword"'\3/' "$filename"

path2='ignite/prod.py'
filename="$path1/$path2"
sed -i  's/\(.NAME.\s*:\s*.\)\([A-Z a-z][0-9 A-Z a-z \! \@ \# \$ \_ \-]*\)\(.\,\)/\1'"$dbname"'\3/' "$filename"
sed -i  's/\(.USER.\s*:\s*.\)\([A-Z a-z][0-9 A-Z a-z \! \@ \# \$ \_ \-]*\)\(.\,\)/\1'"$dbuser"'\3/' "$filename"
sed -i  's/\(.PASSWORD.\s*:\s*.\)\([A-Z a-z][0-9 A-Z a-z \! \@ \# \$ \_ \-]*\)\(.\,\)/\1'"$dbpassword"'\3/' "$filename"
#sed -i  's/\(result\[\"config_password\"\]\s*=\s*\"\)\([A-Z a-z][0-9 A-Z a-z \! \@ \# \$]*\)\(\"\)/\1'"$vmpassword"'\3/' "$filename"

