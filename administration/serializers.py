from rest_framework import serializers

from constants import SERVER_CHOICE


class ServerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    server_ip = serializers.CharField()
    port = serializers.IntegerField()
    secret = serializers.CharField()
    protocol = serializers.ChoiceField(SERVER_CHOICE)
    updated_by = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    date_joined = serializers.DateTimeField(read_only=True)
    is_superuser = serializers.BooleanField()
    last_login = serializers.DateTimeField(read_only=True)


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.CharField()
    is_superuser = serializers.BooleanField()
