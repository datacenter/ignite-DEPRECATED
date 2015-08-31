__author__ = "arunrajms"

from rest_framework import serializers
from resource.models import Switch
from rest_framework.validators import UniqueValidator
import re

TIER_CHOICES = ['Spine','Leaf','Core','Host','Any','any']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value
        
class SwitchSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, \
                                 validators=[UniqueValidator(queryset=Switch.objects.all())])
    model = serializers.CharField(max_length=100,required=True)
    image = serializers.CharField(max_length=100,required=True)
    line_cards = serializers.CharField(max_length=100,required=True)
    slots = serializers.IntegerField()
    tier = serializers.ChoiceField(TIER_CHOICES)
    
    def create(self,validated_data):
        '''
        TBD
        '''
        return Collection.objects.create(**validated_data)   
        
class SwitchGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    model = serializers.CharField(max_length=100,required=True)
    image = serializers.CharField(max_length=100,required=True)
    line_cards = serializers.CharField(max_length=100,required=True)
    slots = serializers.IntegerField()
    tier = serializers.CharField(max_length=100,required=True)