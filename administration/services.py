from django.db import transaction


from serializers import *
import aaaserver
from utils.exception import IgniteException


def get_all_servers():
    server_objs = aaaserver.get_all_servers()
    serializer = ServerSerializer(server_objs, many=True)
    return serializer.data


@transaction.atomic
def add_server(data, username):
    serializer = ServerSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    server = aaaserver.add_server(data, username)
    serializer = ServerSerializer(server)
    return serializer.data


def get_server(id):
    server = aaaserver.get_server(id)
    serializer = ServerSerializer(server)
    return serializer.data


@transaction.atomic
def update_server(data, id, username):
    serializer = ServerSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    server = aaaserver.update_server(data, id, username)
    serializer = ServerSerializer(server)
    return serializer.data


@transaction.atomic
def delete_server(id):
    aaaserver.delete_server(id)


def get_all_users():
    users = aaaserver.get_all_users()
    serializer = UserSerializer(users, many=True)
    return serializer.data


@transaction.atomic
def add_user(data):
    serializer = UserCreateSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    user = aaaserver.add_user(data)
    serializer = UserSerializer(user)
    return serializer.data


def get_user(id):
    user = aaaserver.get_user(id)
    serializer = UserDetailSerializer(user)
    return serializer.data


@transaction.atomic
def update_user(data, id):
    serializer = UserPutSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    user = aaaserver.update_user(data, id)
    serializer = UserSerializer(user)
    return serializer.data


@transaction.atomic
def delete_user(id):
    aaaserver.delete_user(id)
