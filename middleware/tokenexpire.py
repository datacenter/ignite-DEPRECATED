import datetime
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
import json
from rest_framework import status
from rest_framework.authtoken.models import Token


HTTP_AUTH = 'HTTP_AUTHORIZATION'

# session time given in seconds, minutes, hours
SESSION_TIME = datetime.timedelta(hours=2)

LOGIN_PATH = "/auth/login/"


class TokenExpiredMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):
        resp = dict()
        if HTTP_AUTH in request.META:
            if Token.objects.filter(key=request.META[HTTP_AUTH]):
                token = self.process_token(request.META[HTTP_AUTH])
                if token:
                    token.delete()
                    resp["status"] = "Session Expired, Please login again"
                    return JsonResponse(resp, status=status.HTTP_401_UNAUTHORIZED)
            else:
                resp['error'] = "Token not found"
                return JsonResponse(resp, status=status.HTTP_401_UNAUTHORIZED)

    def process_response(self, request, response):
        if str(request.path) == LOGIN_PATH:
            try:
                data = json.loads(response.content)
                token = self.process_token(data['auth_token'])
                if token:
                    user = User.objects.get(pk=token.user_id)
                    old = token.key
                    token.delete()
                    new_token = Token.objects.create(user=user)
                    response.content = response.content.replace(old, new_token.key)
            except:
                pass
        return response

    def process_token(self, token):
        token = Token.objects.get(key=token)
        created = token.created
        now = datetime.datetime.now(timezone.utc)
        diff = now - created
        if SESSION_TIME < diff:
            return token
        return False
