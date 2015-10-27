from rest_framework import serializers
from fabric_profile.models import FabricProfile, ProfileTemplate
from rest_framework.validators import UniqueValidator
import re

PARAM_TYPE_CHOICES = [ 'Fixed', 'Instance', 'Pool', 'Value', 'Autogenerate' ]
CONSTRUCT_TYPE_CHOICES = ['append_ProfileTemplate','append_script']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value
"""
Profile template serializer
"""
class ProfileTemplateSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, validators=[UniqueValidator(queryset=ProfileTemplate.objects.all())])
    group = serializers.CharField(max_length=100,required=True)
    parameters = serializers.CharField(max_length=500,required=False)

    def create(self, validated_data):
        """
        Create and return a new `Profile Template instance, given the validated data.
        """
        return ProfileTemplate.objects.create(**validated_data)
    
    
class ProfileTemplateGetSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=True, validators=[UniqueValidator(queryset=ProfileTemplate.objects.all())])
    group = serializers.CharField(max_length=100,required=True)
    parameters = JSONSerializerField()
    
    
    
class Parameter(serializers.Serializer):

    param_name = serializers.CharField(max_length=100, required=True)
    param_type = serializers.ChoiceField(PARAM_TYPE_CHOICES)
    param_value = serializers.CharField(max_length=100, required=True)

class Construct(serializers.Serializer):

    template_id = serializers.IntegerField(required=True)
    param_list = Parameter(required=True,many=True)


"""
Fabric Profile Serializer
"""

class FabricProfileSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, \
                                 validators=[UniqueValidator(queryset=FabricProfile.objects.all())])
    submit = serializers.CharField(max_length=10)
    construct_list = Construct(required=True,many=True)

    def create(self, validated_data):
        """
        Create and return a new `FabricProfile` instance, given the validated data.
        """
        return FabricProfile.objects.create(**validated_data)


class FabricProfilePutSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=100, required=True)
    submit = serializers.CharField(max_length=10)
    construct_list = Construct(required=True,many=True)

class FabricProfileGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, validators=[UniqueValidator(queryset=FabricProfile.objects.all())])
    submit = serializers.CharField(max_length=10)
    referenced = serializers.IntegerField()
    installed = serializers.IntegerField()
    construct_list = JSONSerializerField()
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    last_modified_by = serializers.CharField()
    used = serializers.IntegerField()