from radiusauth.backends import RADIUSBackend
from django.contrib.auth.models import User

from administration.constants import RADIUS
from administration.models import AAAServer, AAAUser

class RadiusBackend(RADIUSBackend):

    def authenticate(self, username, password):
        server_list = AAAServer.objects.all().filter(protocol=RADIUS)

        for host in server_list:
            server = [host.server_ip, host.port, str(host.secret)]
            result = self._radius_auth(server, username, password)
            if result:
                user = self.get_django_user(username, password)
                # saving valid AAAUser in table, used this while logout
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
