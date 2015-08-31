__author__  = "Rohit N Dubey"

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
import logging
logger = logging.getLogger(__name__)
import re
import pytz
from dateutil.parser import parse  

class RequestValidator(object):

    def __init__(self,metaobj):

        self.meta_obj = metaobj
        self.auth_key = None
        self.get_token = None

    def user_is_exist(self):

        try:
            self.auth_key = self.meta_obj['HTTP_AUTHORIZATION']
            logger.debug("Authorization key: "+str(self.auth_key))
            self.get_token = Token.objects.get(key = self.auth_key)
        except:
            self.get_token = None
            logger.error("Not a valid authorization key")

        return self.get_token
    def invalid_token(self):
        resp = {}
        resp['message'] = 'Invalid Token'
        return resp


def parse_file(file_content):

    param_list = []
    get_parameter_list = re.findall('\$\$[0-9a-zA-Z_]+\$\$',file_content)
    for one_param in get_parameter_list:
        one_param = one_param.strip('$$')
        if one_param not in param_list:
            param_list.append(one_param)
    return param_list


def change_datetime(collec):
    '''
	Accept a orderded list of dict change lastmodified param
    '''
    for coll  in collec:
        for k,v in coll.items():
            if k == 'lastmodified' and v:
                dt = parse(v)
                localtime =  dt.astimezone (pytz.timezone('Asia/Kolkata'))
                coll[k] =  localtime.strftime ("%Y-%m-%d %H:%M:%S")
	
            if k == 'created_date' and v:
                dt = parse(v)
                localtime =  dt.astimezone (pytz.timezone('Asia/Kolkata'))
                coll[k] =  localtime.strftime ("%Y-%m-%d %H:%M:%S")

            if k == 'updated_date' and v:
                dt = parse(v)
                localtime =  dt.astimezone (pytz.timezone('Asia/Kolkata'))
                coll[k] =  localtime.strftime ("%Y-%m-%d %H:%M:%S")
    return collec
