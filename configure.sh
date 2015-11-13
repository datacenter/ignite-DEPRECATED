#!/bin/sh

#Run this file to set UI server configurable parameters
#------------UI Configureable parameters-------------
#Please mention the ip/port on which server is running.
#This script will configure UI server 
#User can also do maual configurations in file /ignite/ignite/disct/scripts/util/settings*.js

ignite_ip=127.0.0.1
ignite_port=8000

#--------------------------------------------------


#------------Script to modify the server settings--

path1=`pwd`
path2='dist/scripts/utils'
setting_filepath="$path1/$path2"
filename=`find "$setting_filepath" -name "setting*"`
sed -i 's/\(\"baseURL\"\s*\:\s*\"http\:\/\/\)\(.*\)\(\"\,\)/\1'"$ignite_ip"':'"$ignite_port"'\3/' "$filename"

