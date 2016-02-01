from rest_framework import serializers

from constants import PARAM_TYPES
from utils.serializers import JSONSerializerField


class ConfigletBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    group = serializers.CharField()
    parameters = JSONSerializerField()
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class ConfigletPostSerializer(serializers.Serializer):

    name = serializers.CharField()
    group = serializers.CharField()


class ConfigletSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    group = serializers.CharField()
    parameters = JSONSerializerField()
    file = serializers.ListField(child=serializers.CharField())
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class ProfileBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.BooleanField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    updated_by = serializers.CharField()


class ProfileSerializer(serializers.Serializer):

    class Construct(serializers.Serializer):

        class Parameter(serializers.Serializer):

            param_name = serializers.CharField()
            param_type = serializers.ChoiceField(PARAM_TYPES)
            param_value = serializers.CharField()

        configlet_id = serializers.IntegerField()
        param_list = Parameter(many=True)

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.BooleanField()
    construct_list = Construct(many=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
