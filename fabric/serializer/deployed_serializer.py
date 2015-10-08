from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from fabric.models import DeployedFabricStats

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value
    

class DeployedFabricGetSerializer(serializers.Serializer):
    fabric_id = serializers.IntegerField()
    fabric_name = serializers.CharField(required = False)
    total_replicas = serializers.ListField(child = serializers.IntegerField())
    
class DeployedFabricDetailGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    fabric_id = serializers.IntegerField()
    replica_num = serializers.IntegerField()
    switch_name = serializers.CharField()
    config_id = serializers.IntegerField()
    config_name = serializers.CharField()
    booted = serializers.BooleanField()
    boot_time = serializers.DateTimeField()
    discoveryrule_id = serializers.IntegerField()
    system_id = serializers.CharField()
    match_type = serializers.CharField()
    configuration_generated = serializers.CharField()
    logs = serializers.CharField()
    
