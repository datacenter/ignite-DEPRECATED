from rest_framework import serializers

from constants import CONSTRUCT_TYPE_OPTIONS, PARAM_TYPES
from utils.serializers import JSONSerializerField


class ConfigletBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    version = serializers.IntegerField()
    group = serializers.CharField()
    type = serializers.ChoiceField(CONSTRUCT_TYPE_OPTIONS)
    parameters = JSONSerializerField()
    configletindex_id = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class ConfigletPostSerializer(serializers.Serializer):

    name = serializers.CharField()
    group = serializers.CharField()
    type = serializers.ChoiceField(CONSTRUCT_TYPE_OPTIONS)


class ConfigletSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    version = serializers.IntegerField()
    configletindex_id = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.CharField()
    type = serializers.ChoiceField(CONSTRUCT_TYPE_OPTIONS)
    parameters = JSONSerializerField()
    file = serializers.ListField(child=serializers.CharField())
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class ProfileBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    version = serializers.IntegerField()
    submit = serializers.BooleanField()
    profileindex_id = serializers.PrimaryKeyRelatedField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    updated_by = serializers.CharField()


class ConstructSerializer(serializers.Serializer):

    class Parameter(serializers.Serializer):

        param_name = serializers.CharField()
        param_type = serializers.ChoiceField(PARAM_TYPES)
        param_value = serializers.CharField()

    configletindex_id = serializers.IntegerField()
    param_list = Parameter(many=True)
    version = serializers.IntegerField()


class ProfilePostSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.BooleanField()
    construct_list = ConstructSerializer(many=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    new_version = serializers.BooleanField()


class ProfileSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    version = serializers.IntegerField()
    submit = serializers.BooleanField()
    construct_list = ConstructSerializer(many=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    profileindex_id = serializers.PrimaryKeyRelatedField(read_only=True)


class ConfigIndexPutSerializer(serializers.Serializer):
    new_version = serializers.CharField()


class AllProfilesSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    version = serializers.IntegerField()
