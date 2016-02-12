from rest_framework import serializers

from utils.serializers import JSONSerializerField
from constants import POOL_TYPES, SCOPE_OPTIONS, ROLE_OPTIONS


class PoolSerializer(serializers.Serializer):

    class PoolEntrySerializer(serializers.Serializer):

        value = serializers.CharField()
        assigned = serializers.CharField()
        updated = serializers.DateTimeField(read_only=True)

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    type = serializers.ChoiceField(POOL_TYPES)
    scope = serializers.ChoiceField(SCOPE_OPTIONS)
    role = serializers.ChoiceField(ROLE_OPTIONS)
    blocks = JSONSerializerField()
    entries = PoolEntrySerializer(required=False, many=True)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    used = serializers.IntegerField(required=False)
    available = serializers.IntegerField(required=False)


class PoolPostSerializer(serializers.Serializer):

    class BlockSerializer(serializers.Serializer):
        start = serializers.CharField()
        end = serializers.CharField()

    name = serializers.CharField()
    type = serializers.ChoiceField(POOL_TYPES)
    scope = serializers.ChoiceField(SCOPE_OPTIONS)
    role = serializers.ChoiceField(ROLE_OPTIONS)
    blocks = BlockSerializer(many=True)

class PoolPutSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
