from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from fabric.models import Fabric

PROTOCOL_LIST = ['http', 'scp', 'ftp']

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class Switch_profileSerializers(serializers.Serializer):
    switch_id = serializers.CharField(max_length=100)
    profile_id = serializers.IntegerField()

 
class ProfilesSerializer(serializers.Serializer):
    leaf_profile = serializers.IntegerField()
    spine_profile = serializers.IntegerField()
    switch_profile = Switch_profileSerializers(many = True)


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
    image_details = JSONSerializerField()
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    #profiles = JSONSerializerField()

class ConfigurationSerializer(serializers.Serializer):
    name = serializers.CharField(required = True)
    configuration_id = serializers.IntegerField(required = True)
    image_name = serializers.CharField(required = False)

class SystemIdSerializer(serializers.Serializer):
    name = serializers.CharField(required = True)
    system_id = serializers.CharField(required = True)
    
class ImageDetailSerializer(serializers.Serializer):
    leaf_switch = serializers.CharField(required = True)
    spine_switch = serializers.CharField(required = True)
    
class FabricPutSerializer(serializers.Serializer):
    name = serializers.CharField()
    topology_id = serializers.IntegerField()
    locked = serializers.IntegerField()
    instance = serializers.IntegerField()
    validate = serializers.IntegerField()
    submit = serializers.CharField(max_length=10)
    config_json = ConfigurationSerializer(required = True, many = True)
    system_id = SystemIdSerializer(required = False, many = True)
    image_details = ImageDetailSerializer(required=False)
    #profiles = ProfilesSerializer(required=False)
    
class FabricSerializer(serializers.Serializer):
    name = serializers.CharField(validators=[UniqueValidator(queryset=Fabric.objects.all())])
    topology_id = serializers.IntegerField()
    locked = serializers.IntegerField()
    instance = serializers.IntegerField()
    validate = serializers.IntegerField()
    submit = serializers.CharField(max_length=10)
    config_json = ConfigurationSerializer(required = True, many = True)
    system_id = SystemIdSerializer(required = False, many = True)
    image_details = ImageDetailSerializer(required=False)
    #profiles = ProfilesSerializer(required=False)

class FabricRuleDBGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    local_node =  serializers.CharField()
    remote_node =  serializers.CharField()
    remote_port =  serializers.CharField()
    local_port =  serializers.CharField()
    action = serializers.IntegerField()

class ImagePostSerializer(serializers.Serializer):
    image_profile_name = serializers.CharField()
    image = serializers.CharField()
    imageserver_ip = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    access_protocol = serializers.ChoiceField(PROTOCOL_LIST)
