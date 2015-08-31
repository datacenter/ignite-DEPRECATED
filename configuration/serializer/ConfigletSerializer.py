__author__  = "Rohit N Dubey"


from rest_framework import serializers
from configuration.models import Configlet
from rest_framework.validators import UniqueValidator
import re

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class ConfigletSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, validators=[UniqueValidator(queryset=Configlet.objects.all())])
    config_type = serializers.CharField(max_length=100,required=True)
    group = serializers.CharField(max_length=100,required=True)
    parameters = serializers.CharField(max_length=500,required=False)


    def create(self, validated_data):
        """
        Create and return a new `Configlet` instance, given the validated data.
        """
        return Configlet.objects.create(**validated_data)


class ConfigletGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, validators=[UniqueValidator(queryset=Configlet.objects.all())])
    config_type = serializers.CharField(max_length=100,required=True)
    group = serializers.CharField(max_length=100,required=True)
    parameters = JSONSerializerField()
