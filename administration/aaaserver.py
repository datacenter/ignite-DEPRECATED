from django.contrib.auth.models import User

from constants import *
from models import AAAServer, AAAUser
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_servers():
    return AAAServer.objects.all()


def get_all_users():
    aaa_id_list = AAAUser.objects.values_list('user_id', flat=True).distinct()
    if aaa_id_list:
        return User.objects.all().exclude(id=aaa_id_list)
    return User.objects.all()


def add_server(data, username):
    server = AAAServer()
    return _add_server(data, server, username)


def get_server(id):
    return AAAServer.objects.get(pk=id)


def update_server(data, id, username):
    server = get_server(id)
    return _add_server(data, server, username)


def delete_server(id):
    get_server(id).delete()


def _add_server(data, server, username):
    server.server_ip = data[SERVER]
    server.port = data[PORT]
    server.secret = data[SECRET]
    server.protocol = data[PROTOCOL]
    server.updated_by = username
    server.save()
    return server


def add_user(data):
    user = User()
    user.username = data[USERNAME]
    user.set_password(data[PASSWORD])
    user.email = data[EMAIL]
    user.is_superuser = data[IS_SUPERUSER]
    user.save()
    return user


def delete_user(id):
    user = User.objects.get(id=id)
    if user.username == ADMIN:
        raise IgniteException(ERR_USER_ADMIN)
    user.delete()
