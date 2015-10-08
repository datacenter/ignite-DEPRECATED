__author__  = "Rohit N Dubey"


from rest_framework import serializers
from configuration.models import Configuration
from rest_framework.validators import UniqueValidator
import re

PARAM_TYPE_CHOICES = [ 'Fixed', 'Instance', 'Pool', 'Value', 'Autogenerate' ]
CONSTRUCT_TYPE_CHOICES = ['append_configlet','append_script']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class Parameter(serializers.Serializer):

    param_name = serializers.CharField(max_length=100, required=True)
    param_type = serializers.ChoiceField(PARAM_TYPE_CHOICES)
    param_value = serializers.CharField(max_length=100, required=True)

class Construct(serializers.Serializer):

    construct_type = serializers.ChoiceField(CONSTRUCT_TYPE_CHOICES)
    configlet_id = serializers.IntegerField(required=True)
    param_list = Parameter(required=True,many=True)

class ConfigurationSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, \
                                 validators=[UniqueValidator(queryset=Configuration.objects.all())])
    submit = serializers.CharField(max_length=10)
    construct_list = Construct(required=True,many=True)

    def create(self, validated_data):
        """
        Create and return a new `configuration` instance, given the validated data.
        """
        return Configuration.objects.create(**validated_data)


class ConfigurationPutSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=100, required=True)
    submit = serializers.CharField(max_length=10)
    construct_list = Construct(required=True,many=True)

class ConfigurationGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, validators=[UniqueValidator(queryset=Configuration.objects.all())])
    submit = serializers.CharField(max_length=10)
    referenced = serializers.IntegerField()
    installed = serializers.IntegerField()
    construct_list = JSONSerializerField()
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
