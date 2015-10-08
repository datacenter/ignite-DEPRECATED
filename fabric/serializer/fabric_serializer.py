from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from fabric.models import Fabric

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value


class FabricGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    locked = serializers.IntegerField() 
    submit = serializers.CharField(max_length=10)
    validate = serializers.IntegerField()
    booted = serializers.IntegerField()
    instance = serializers.IntegerField()
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()

class FabricGetDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    locked = serializers.IntegerField() 
    submit = serializers.CharField(max_length=10)
    validate = serializers.IntegerField()
    booted = serializers.IntegerField()
    instance = serializers.IntegerField()
    config_json = JSONSerializerField()
    system_id = JSONSerializerField() 
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()


class ConfigurationSerializer(serializers.Serializer):
    name = serializers.CharField(required = True)
    configuration_id = serializers.IntegerField(required = True)
    image_name = serializers.CharField(required = False)

class SystemIdSerializer(serializers.Serializer):
    name = serializers.CharField(required = True)
    system_id = serializers.CharField(required = True)
    
class FabricPutSerializer(serializers.Serializer):
    name = serializers.CharField()
    topology_id = serializers.IntegerField()
    locked = serializers.IntegerField()
    instance = serializers.IntegerField()
    validate = serializers.IntegerField()
    submit = serializers.CharField(max_length=10)
    config_json = ConfigurationSerializer(required = True, many = True)
    system_id = SystemIdSerializer(required = False, many = True)

class FabricSerializer(serializers.Serializer):
    name = serializers.CharField(validators=[UniqueValidator(queryset=Fabric.objects.all())])
    topology_id = serializers.IntegerField()
    locked = serializers.IntegerField()
    instance = serializers.IntegerField()
    validate = serializers.IntegerField()
    submit = serializers.CharField(max_length=10)
    config_json = ConfigurationSerializer(required = True, many = True)
    system_id = SystemIdSerializer(required = False, many = True)


class FabricRuleDBGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    local_node =  serializers.CharField()
    remote_node =  serializers.CharField()
    remote_port =  serializers.CharField()
    local_port =  serializers.CharField()
    action = serializers.IntegerField()

