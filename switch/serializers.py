from rest_framework import serializers

from constants import *
from fabric.constants import TIER_NAMES
from utils.serializers import JSONSerializerField


class PortGroupSerializer(serializers.Serializer):

    num_ports = serializers.IntegerField(min_value=1, max_value=96)
    speed = serializers.ChoiceField(PORT_SPEEDS)
    transceiver = serializers.ChoiceField(TRANSCEIVERS)
    role = serializers.ChoiceField(PORT_ROLES)


class LineCardSerializer(serializers.Serializer):

    class LineCardDataSerializer(serializers.Serializer):
        port_groups = PortGroupSerializer(many=True)

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    lc_type = serializers.ChoiceField(LC_TYPES)
    lc_data = LineCardDataSerializer()
    lc_info = JSONSerializerField(read_only=True)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class LineCardPutSerializer(serializers.Serializer):

    class LineCardDataSerializer(serializers.Serializer):
        port_groups = PortGroupSerializer(many=True)

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    lc_type = serializers.ChoiceField(LC_TYPES)
    lc_data = LineCardDataSerializer()
    lc_info = JSONSerializerField(read_only=True)


class SwitchSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    base_model = serializers.CharField()
    switch_type = serializers.CharField()
    switch_data = JSONSerializerField()
    switch_info = JSONSerializerField()
    booted_with_success = serializers.IntegerField(read_only=True)
    booted_with_fail = serializers.IntegerField(read_only=True)
    boot_in_progress = serializers.IntegerField(read_only=True)
    updated_by = serializers.CharField()
    # meta = JSONSerializerField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class SwitchFixedSerializer(serializers.Serializer):

    class SwitchDataSerializer(serializers.Serializer):
        tiers = serializers.ListField(child=serializers.ChoiceField(TIER_NAMES))
        port_groups = PortGroupSerializer(many=True)
        module_id = serializers.IntegerField(required=False)

    name = serializers.CharField()
    base_model = serializers.CharField()
    switch_type = serializers.ChoiceField([FIXED])
    switch_data = SwitchDataSerializer()


class SwitchChassisSerializer(serializers.Serializer):

    class SwitchDataSerializer(serializers.Serializer):

        class SlotSerializer(serializers.Serializer):

            slot_num = serializers.IntegerField(min_value=1, max_value=16)
            lc_id = serializers.IntegerField()

        tiers = serializers.ListField(child=serializers.ChoiceField(TIER_NAMES))
        num_slots = serializers.IntegerField()
        slots = SlotSerializer(many=True)

    name = serializers.CharField()
    base_model = serializers.CharField()
    switch_type = serializers.ChoiceField([CHASSIS])
    switch_data = SwitchDataSerializer()
