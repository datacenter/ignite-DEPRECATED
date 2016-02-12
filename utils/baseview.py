from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from exception import TokenException, UnauthorizedException

import logging
logger = logging.getLogger(__name__)

HTTP_AUTH = 'HTTP_AUTHORIZATION'


class BaseView(APIView):

    def dispatch(self, request, *args, **kwargs):
        self.token_validator(request.META)
        return super(BaseView, self).dispatch(request, *args, **kwargs)

    def token_validator(self, obj):
        if HTTP_AUTH not in obj:
            raise TokenException("Token is not provided")

        auth_key = obj[HTTP_AUTH]

        try:
            self.username = Token.objects.get(key=auth_key).user.username
            #logger.debug('user name : ' + self.username)
        except:
            raise TokenException("Invalid Token")


class AdminView(APIView):

    def dispatch(self, request, *args, **kwargs):
        self.token_validator(request.META)
        return super(AdminView, self).dispatch(request, *args, **kwargs)

    def token_validator(self, obj):
        if HTTP_AUTH not in obj:
            raise TokenException("Token is not provided")

        auth_key = obj[HTTP_AUTH]

        try:
            self.username = Token.objects.get(key=auth_key).user.username
            user_obj = User.objects.get(username=self.username)
        except:
            raise TokenException("Invalid Token")

        if not user_obj.is_superuser:
            raise UnauthorizedException("Unauthorised access")
