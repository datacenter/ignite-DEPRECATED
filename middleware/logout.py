from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from administration.models import AAAUser

PATH = "/auth/logout/"


class LogoutMiddleWare(object):
    def __init__(self):
        pass

    def process_request(self, request):
        resp = {}
        if str(request.path) == PATH:
            try:
                key = request.META['HTTP_AUTHORIZATION']
                token = Token.objects.get(key=key)
                id = token.user_id
                token.delete()
                #  check for logged-in user is either radius or tacacs,
                # then delete entry from user table
                if AAAUser.objects.filter(user_id=id):
                    User.objects.get(pk=id).delete()
                msg = "successfully logedout"
                resp['status'] = msg
                return JsonResponse(resp, status=status.HTTP_401_UNAUTHORIZED)

            except:
                resp['error'] = "Token not found"
                return JsonResponse(resp, status=status.HTTP_401_UNAUTHORIZED)
