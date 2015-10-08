from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from fabric.models import Topology
from fabric.serializer.fabric_serializer import ConfigurationSerializer

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_interemote_nodeal_value(self, data):
        return data
    def to_representation(self, value):
        return value


class TopologyGetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.CharField(max_length=10)
    used = serializers.IntegerField()
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()

class TopologyGetDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.CharField(max_length=10)
    topology_json = JSONSerializerField()
    config_json = JSONSerializerField()
    defaults = JSONSerializerField()

class LinkSerializer(serializers.Serializer):
    id_1 = serializers.CharField()
    id_2 = serializers.CharField()
    switch_1 = serializers.CharField()
    switch_2 = serializers.CharField()
    port_list_1 = serializers.ListField(child=serializers.CharField())
    port_list_2 = serializers.ListField(child=serializers.CharField())
    link_type = serializers.CharField()

class SwitchSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    type = serializers.CharField()

class DefaultSerializer(serializers.Serializer):
    spine_switch = serializers.CharField(required = True)
    leaf_switch = serializers.CharField(required = True)
    spine_leaf_link = serializers.CharField(required = True)
    spine_leaf_link_index = serializers.CharField(required = True)
    
class TopologyComponentsSerializer(serializers.Serializer):
    core_list = SwitchSerializer(required = False,many= True)
    spine_list = SwitchSerializer(required = True,many= True)
    leaf_list = SwitchSerializer(required = True,many= True)
    link_list = LinkSerializer(required = False,many= True)

class TopologySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(validators=[UniqueValidator(queryset=Topology.objects.all())])
    submit = serializers.CharField(max_length=10)
    topology_json = TopologyComponentsSerializer(required = True,many= False)
    config_json = ConfigurationSerializer(required = False, many = True)
    defaults = DefaultSerializer(required = False, many = False)
    
class TopologyPutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.CharField(max_length=10)
    topology_json = TopologyComponentsSerializer(required = True,many= False)
    config_json = ConfigurationSerializer(required = False, many = True)
    defaults = DefaultSerializer(required = True, many = False)
