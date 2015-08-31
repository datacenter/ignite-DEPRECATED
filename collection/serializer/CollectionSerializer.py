__author__ = "arunrajms"

from rest_framework import serializers
from collection.models import Collection
from rest_framework.validators import UniqueValidator
import re

TYPE_CHOICES = ['Integer','IP','IPv6','AutoGenerate','Vlan','MgmtIP']
PUT_TYPE_CHOICES = ['Integer','IP','IPv6','Vlan','MgmtIP']
SCOPE_CHOICES = ['global','fabric','switch']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class CollectionRange(serializers.Serializer):

    start = serializers.CharField(max_length=24, required=True)
    end = serializers.CharField(max_length=24, required=True)

class CollectionSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True, \
                                 validators=[UniqueValidator(queryset=Collection.objects.all())])
    type = serializers.ChoiceField(TYPE_CHOICES)
    range = CollectionRange(required=False, many=True)
    available = serializers.IntegerField(read_only=True)
    used = serializers.IntegerField(read_only=True)
    scope = serializers.ChoiceField(SCOPE_CHOICES)

    def create(self,validated_data):
        '''
        TBD
        '''
        return Collection.objects.create(**validated_data)        
        
class CollectionGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    type = serializers.CharField(max_length=100)
    range = JSONSerializerField()#serializers.CharField(max_length=500)
    used = serializers.IntegerField()
    available = serializers.IntegerField()
    scope = serializers.CharField()
    
class CollectionGetDetailSerializer(serializers.Serializer):

    value = serializers.CharField(max_length=100)
    assigned = serializers.CharField(max_length=100,required=False)
    lastmodified = serializers.CharField(max_length=100)
    
class CollectionPutSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100,required=True)
    type = serializers.ChoiceField(PUT_TYPE_CHOICES)
    range = CollectionRange(required=False, many=True)
    #available = serializers.IntegerField(read_only=True)
    #used = serializers.IntegerField(read_only=True)
    #scope = serializers.ChoiceField(SCOPE_CHOICES)

    def create(self,validated_data):
        '''
        TBD
        '''
        return Collection.objects.create(**validated_data)   