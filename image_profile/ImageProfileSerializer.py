from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from image_profile.models import ImageProfile

PROTOCOL_LIST = ['http', 'scp', 'ftp']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class ImageProfileGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    image_profile_name = JSONSerializerField()
    image = JSONSerializerField()
    imageserver_ip = serializers.CharField(max_length=24)
    username = JSONSerializerField()
    password = JSONSerializerField()
    access_protocol = serializers.ChoiceField(PROTOCOL_LIST)

class ImageProfilePostSerializer(serializers.Serializer):
    image_profile_name = serializers.CharField(validators=[UniqueValidator(queryset=ImageProfile.objects.all())])
    image = serializers.CharField()
    imageserver_ip = serializers.CharField(max_length=24)
    username = serializers.CharField()
    password = serializers.CharField()
    access_protocol = serializers.ChoiceField(PROTOCOL_LIST)

class ImageProfilePutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    image_profile_name = serializers.CharField()
    image = serializers.CharField()
    imageserver_ip = serializers.CharField(max_length=24)
    username = serializers.CharField()
    password = serializers.CharField()
    access_protocol = serializers.ChoiceField(PROTOCOL_LIST)

