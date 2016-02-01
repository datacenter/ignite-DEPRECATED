from rest_framework import serializers
from utils.serializers import JSONSerializerField
from constants import PARAM_TYPE_CHOICES, CONSTRUCT_TYPE_CHOICES


class FeatureSerializer(serializers.Serializer):

    name = serializers.CharField()
    group = serializers.CharField()


class FeatureGetBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = JSONSerializerField()
    group = JSONSerializerField()
    parameters = JSONSerializerField()
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class FeatureGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = JSONSerializerField()
    group = JSONSerializerField()
    parameters = JSONSerializerField()
    updated_by = serializers.CharField()
    file = serializers.ListField(child=serializers.CharField())


class ProfileSerializer(serializers.Serializer):

    class Construct(serializers.Serializer):

        class Parameter(serializers.Serializer):
            param_name = serializers.CharField
            param_type = serializers.ChoiceField(PARAM_TYPE_CHOICES)
            param_value = serializers.CharField

        template_id = serializers.IntegerField()
        param_list = Parameter(many=True)

    name = serializers.CharField()
    submit = serializers.BooleanField()
    construct_list = Construct(many=True)


class ProfileGetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = JSONSerializerField()
    submit = serializers.BooleanField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    construct_list = JSONSerializerField()
    updated_by = serializers.CharField()


class ProfileGetAllSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = JSONSerializerField()
    submit = serializers.BooleanField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    updated_by = serializers.CharField()
