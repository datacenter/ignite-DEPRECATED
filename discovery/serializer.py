from rest_framework import serializers


from models import DiscoveryRule
from utils.serializers import JSONSerializerField
from constants import CHOICES, MATCH_CHOICES


class DiscoveryRuleSerializer(serializers.Serializer):
    class SubRules(serializers.Serializer):
        rn_condition = serializers.ChoiceField(CHOICES)
        rn_string = serializers.CharField(max_length=100, allow_blank=True)
        rp_condition = serializers.ChoiceField(CHOICES)
        rp_string = serializers.CharField(max_length=100, allow_blank=True)
        lp_condition = serializers.ChoiceField(CHOICES)
        lp_string = serializers.CharField(max_length=100, allow_blank=True)
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    priority = serializers.IntegerField(max_value=100, required=False)
    config = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.PrimaryKeyRelatedField(read_only=True)
    workflow = serializers.PrimaryKeyRelatedField(read_only=True)
    subrules = SubRules(many=True)
    match = serializers.ChoiceField(MATCH_CHOICES)


class DiscoveryRuleSerialIDSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    priority = serializers.IntegerField(required=False)
    config = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.PrimaryKeyRelatedField(read_only=True)
    workflow = serializers.PrimaryKeyRelatedField(read_only=True)
    subrules = serializers.ListField(child=serializers.CharField())
    match = serializers.ChoiceField(MATCH_CHOICES)


class DiscoveryRuleGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    priority = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    config = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.PrimaryKeyRelatedField(read_only=True)
    workflow = serializers.PrimaryKeyRelatedField(read_only=True)
    match = serializers.ChoiceField(MATCH_CHOICES)
    updated_by = serializers.CharField()
    #subrules = JSONSerializerField()


class DiscoveryRuleGetDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    priority = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    config = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.PrimaryKeyRelatedField(read_only=True)
    workflow = serializers.PrimaryKeyRelatedField(read_only=True)
    match = serializers.ChoiceField(MATCH_CHOICES)
    subrules = JSONSerializerField()
