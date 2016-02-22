from constants import *

from rest_framework import serializers

from fabric.constants import MATCH_TYPES


class IgniteRequestPostSerializer(serializers.Serializer):

    class NeighborSerializer(serializers.Serializer):

        remote_node = serializers.CharField(allow_blank=True, required=False)
        remote_port = serializers.CharField(allow_blank=True, required=False)
        local_port = serializers.CharField(allow_blank=True, required=False)

    serial_num = serializers.CharField()
    neighbor_list = NeighborSerializer(many=True)


class BootstrapSwitchSerializer(serializers.Serializer):

    class TopologySerializer(serializers.Serializer):

        name = serializers.CharField()

    class SwitchBootDetailSerializer(serializers.Serializer):

        class DiscoveryRuleSerializer(serializers.Serializer):

            name = serializers.CharField()

        boot_status = serializers.CharField()
        boot_time = serializers.DateTimeField()
        match_type = serializers.ChoiceField(MATCH_TYPES, required=False)
        discovery_rule = serializers.IntegerField()

    id = serializers.IntegerField()
    name = serializers.CharField()
    serial_num = serializers.CharField()
    topology = TopologySerializer()
    boot_detail = SwitchBootDetailSerializer()


class SwitchBootStatusPostSerializer(serializers.Serializer):

    serial_num = serializers.CharField()
    status = serializers.BooleanField()


class RmaSerializer(serializers.Serializer):

    match = serializers.ChoiceField(RMA_MATCH)
    switch_detail = BootstrapSwitchSerializer(required=False)
    rule = serializers.IntegerField(required=False)


class UpdateRmaSerializer(serializers.Serializer):

    old_serial_num = serializers.CharField()
    new_serial_num = serializers.CharField()
