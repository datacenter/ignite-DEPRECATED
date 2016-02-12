from ctypes import *
from django.contrib.auth.models import User
import os
import sys
import platform

from administration.constants import TACACS
from administration.models import AAAServer, AAAUser
from ignite.settings import BASE_DIR

import logging
logger = logging.getLogger(__name__)


class TacacsBackend(object):

    def authenticate(self, username, password):
        server_list = AAAServer.objects.all().filter(protocol=TACACS)
	if server_list is None:
		return None

        is_64bits = sys.maxsize > 2**32
	linux_distribution = str(platform.linux_distribution()).lower()
	if linux_distribution.find("ubuntu") != -1: 
        	if is_64bits:
            		lib1 = CDLL(os.path.join(BASE_DIR, "administration/Ubuntu_64bit_libtac.so.2"))
            		lib = CDLL(os.path.join(BASE_DIR, "administration/Ubuntu_64bit_pam_tacplus.so"))
        	else:
            		lib1 = CDLL(os.path.join(BASE_DIR, "administration/Ubuntu_32bit_libtac.so.2"))
            		lib = CDLL(os.path.join(BASE_DIR, "administration/Ubuntu_32bit_pam_tacplus.so"))
	elif linux_distribution.find("centos") != -1:
		if is_64bits:
                        lib1 = CDLL(os.path.join(BASE_DIR, "administration/CentOS_64bit_libtac.so.2"))
                        lib = CDLL(os.path.join(BASE_DIR, "administration/CentOS_64bit_pam_tacplus.so"))
                else:
                        lib1 = CDLL(os.path.join(BASE_DIR, "administration/CentOS_32bit_libtac.so.2"))
                        lib = CDLL(os.path.join(BASE_DIR, "administration/CentOS_32bit_pam_tacplus.so"))
	else:
		logger.debug("Unsupported linux distribution")
		return None

        for host in server_list:
            result = lib.authenticate_tacacs(str(username), str(password), str(host.server_ip), host.port, str(host.secret))
            if not result:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User(username=username)
                    user.set_password(password)
                    user.save()

                aaa = AAAUser()
                aaa.username = username
                aaa.user = user
                aaa.save()
                return user

        return None

    def get_user(self, user_id):
        """
        Get the user with the ID of `user_id`. Authentication backends must
        implement this method.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
