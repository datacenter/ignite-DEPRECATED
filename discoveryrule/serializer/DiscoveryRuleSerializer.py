__author__ = "arunrajms"

from rest_framework import serializers
from discoveryrule.models import DiscoveryRule
from rest_framework.validators import UniqueValidator
import re

CHOICES = ['contain','no_contain','match','no_match','exact','any','oneof','none']
MATCH_CHOICES = ['all','any','All','Any','serial_id','ALL','ANY']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

        
class SubRules(serializers.Serializer):

    rn_condition = serializers.ChoiceField(CHOICES)
    rn_string = serializers.CharField(max_length=100,required=True)    
    rp_condition = serializers.ChoiceField(CHOICES)
    rp_string = serializers.CharField(max_length=100,required=True)
    lp_condition = serializers.ChoiceField(CHOICES)
    lp_string = serializers.CharField(max_length=100,required=True)
    
class DiscoveryRuleSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, \
                                 validators=[UniqueValidator(queryset=DiscoveryRule.objects.all())])
    priority = serializers.IntegerField(required=False)
    #user_id = serializers.IntegerField(required=False)
    config_id = serializers.IntegerField()
    subrules = SubRules(required=True,many=True)
    match = serializers.ChoiceField(MATCH_CHOICES)
    
    def create(self,validated_data):
        '''
        TBD
        '''
        return DiscoveryRule.objects.create(**validated_data)
        
class DiscoveryRuleSerialIDSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, \
                                 validators=[UniqueValidator(queryset=DiscoveryRule.objects.all())])
    priority = serializers.IntegerField(required=False)
    #user_id = serializers.IntegerField(required=False)
    config_id = serializers.IntegerField()
    subrules = serializers.ListField(child=serializers.CharField(max_length=100))
    match = serializers.ChoiceField(MATCH_CHOICES)
    
    def create(self,validated_data):
        '''
        TBD
        '''
        return DiscoveryRule.objects.create(**validated_data)
  
class DiscoveryRulePutSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    priority = serializers.IntegerField(required=False)
    #user_id = serializers.IntegerField(required=False)
    config_id = serializers.IntegerField()
    subrules = SubRules(required=True,many=True)
    match = serializers.CharField(max_length=10,required=True)
    
    def create(self,validated_data):
        '''
        TBD
        '''
        return DiscoveryRule.objects.create(**validated_data)
        
  
class DiscoveryRuleIDPutSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    priority = serializers.IntegerField(required=False)
    config_id = serializers.IntegerField()
    subrules = serializers.ListField(child=serializers.CharField(max_length=100))
    match = serializers.CharField(max_length=10,required=True)
    
    def create(self,validated_data):
        '''
        TBD
        '''
        return DiscoveryRule.objects.create(**validated_data)
        


    
    
class DiscoveryRuleGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    priority = serializers.IntegerField()
    used_count = serializers.IntegerField()
    user_id = serializers.IntegerField()
    created_date = serializers.DateTimeField()
    last_modified = serializers.DateTimeField()
    config_id = serializers.IntegerField()
    match = serializers.CharField(max_length=10,required=True)
    #subrules = JSONSerializerField()
    
class DiscoveryRuleGetDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    priority = serializers.IntegerField()
    used_count = serializers.IntegerField()
    user_id = serializers.IntegerField()
    created_date = serializers.DateTimeField()
    last_modified = serializers.DateTimeField()
    config_id = serializers.IntegerField()
    match = serializers.CharField(max_length=10,required=True)
    subrules = JSONSerializerField()
    
    
    
    
    