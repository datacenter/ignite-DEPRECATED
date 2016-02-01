from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token

from ignite.settings import LOGGING

import logging

HTTP_AUTH = 'HTTP_AUTHORIZATION'


class LoggingMiddleware(object):
    def __init__(self):
        pass
        # arguably poor taste to use django's logger

    def process_request(self, request):
        FORMAT = "[%(asctime)s] %(levelname)s " + "[user:switch]" + \
                 " [%(name)s:%(lineno)s] %(message)s"
        if HTTP_AUTH in request.META:
            try:
                token = Token.objects.get(key=request.META[HTTP_AUTH])
                user_name = "[user:" + str(token.user) + "]"
                FORMAT = "[%(asctime)s] %(levelname)s " + user_name + \
                         " [%(name)s:%(lineno)s] %(message)s"
            except:
                msg = "Token does not exist"
                code = status.HTTP_401_UNAUTHORIZED
                return JsonResponse({'err_msg': msg}, status=code)
        LOGGING['formatters']['verbose']['format'] = FORMAT
        logging.config.dictConfig(LOGGING)
