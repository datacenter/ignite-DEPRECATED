from rest_framework import serializers

from constants import ACCESS_PROTOCOLS
from utils.serializers import JSONSerializerField


class TaskBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    parameters = JSONSerializerField()
    updated_by = serializers.CharField()
    desc = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class TaskSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    handler = serializers.CharField()
    desc = serializers.CharField()
    function = serializers.CharField()
    location_server_ip = serializers.CharField()
    location_server_user = serializers.CharField()
    location_server_password = serializers.CharField()
    location_access_protocol = serializers.ChoiceField(ACCESS_PROTOCOLS)
    parameters = JSONSerializerField()


class WorkflowBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.BooleanField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    updated_by = serializers.CharField()


class WorkflowSerializer(serializers.Serializer):

    class Task(serializers.Serializer):

        task_id = serializers.IntegerField()
        parameters = JSONSerializerField()

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    submit = serializers.BooleanField()
    task_list = Task(many=True)
