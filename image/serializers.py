from django.core.validators import validate_ipv4_address
from rest_framework import serializers


ACCESS_PROTOCOLS = ["ftp", "tftp", "scp", "http"]


class ImageProfileSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    profile_name = serializers.CharField()
    system_image = serializers.CharField(allow_null=True)
    epld_image = serializers.CharField(allow_null=True)
    kickstart_image = serializers.CharField(allow_null=True)
    image_server_ip = serializers.CharField(validators=[validate_ipv4_address])
    image_server_username = serializers.CharField()
    image_server_password = serializers.CharField()
    access_protocol = serializers.ChoiceField(ACCESS_PROTOCOLS)


class ImageProfilePutSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    profile_name = serializers.CharField()
    system_image = serializers.CharField()
    epld_image = serializers.CharField()
    kickstart_image = serializers.CharField()
    image_server_ip = serializers.CharField(validators=[validate_ipv4_address])
    image_server_username = serializers.CharField()
    image_server_password = serializers.CharField()
    access_protocol = serializers.ChoiceField(ACCESS_PROTOCOLS)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
