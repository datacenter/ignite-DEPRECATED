from rest_framework import serializers

from fabric.models import Switch
from pool.models import PoolEntry
from models import *
from utils.serializers import JSONSerializerField


JOB_TYPES = ['switch_upgrade', 'epld_upgrade', 'custom', 'import_config']
PARAM_TYPES = ['fixed', 'eval']


class GroupSwitchPostSerializer(serializers.Serializer):
    switch_id = serializers.IntegerField()


class GroupPostSerializer(serializers.Serializer):
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    switch_list = GroupSwitchPostSerializer(many=True)


class GroupBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    fabric = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class GroupDetailSerializer(serializers.Serializer):

    class GroupSwitchSerializer(serializers.ModelSerializer):
        switch_id = serializers.IntegerField(source='grp_switch.id', read_only=True)
        switch_name = serializers.CharField(source='grp_switch.name', read_only=True)
        serial_num = serializers.CharField(source='grp_switch.serial_num', read_only=True)
        fabric_name = serializers.CharField(source='grp_switch.topology.name', read_only=True)
        switch_ip = serializers.CharField(source='grp_switch.mgmt_ip', read_only=True)

        class Meta:
            model = GroupSwitch
            fields = ('id', 'switch_id', 'switch_name', 'switch_ip', 'serial_num', 'fabric_name')
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    fabric = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    switch_list = GroupSwitchSerializer(many=True)


class ParamSerializer(serializers.Serializer):
    param_name = serializers.CharField()
    param_type = serializers.ChoiceField(PARAM_TYPES)
    param_val = serializers.CharField()


class JobPostSerializer(serializers.Serializer):
    class JobSerializer(serializers.Serializer):
        group_id = serializers.IntegerField()
        image_id = serializers.IntegerField()
        run_size = serializers.IntegerField(min_value=1, max_value=5)
        retry_count = serializers.IntegerField(min_value=0, max_value=3)
        file_name = serializers.CharField(required=False)
        function = serializers.CharField(required=False)
        #params = JSONSerializerField(required=False)
        params = serializers.ListField(required=False, child=ParamSerializer(required=False))
        type = serializers.ChoiceField(choices=JOB_TYPES)
        failure_action_grp = serializers.ChoiceField(choices=['continue', 'abort'])
        failure_action_ind = serializers.ChoiceField(choices=['continue', 'abort'])
    name = serializers.CharField()
    schedule = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    tasks = JobSerializer(many=True)


class JobBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    schedule = serializers.DateTimeField()
    status = serializers.CharField()
    ctime = serializers.DateTimeField(required=False)
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class JobDetailSerializer(serializers.Serializer):
    class TaskSerializer(serializers.Serializer):
        class GroupSerializer(serializers.Serializer):
            class SwitchSerializer(serializers.Serializer):
                id = serializers.IntegerField()
                name = serializers.CharField()
                status = serializers.CharField(required=False)
                log = serializers.CharField(required=False)
                ctime = serializers.CharField(required=False)
            group_name = serializers.CharField()
            username = serializers.CharField()
            password = serializers.CharField()
            switches = SwitchSerializer(many=True)
        status = serializers.CharField(required=False)
        group_id = serializers.IntegerField()
        image_id = serializers.IntegerField()
        switch_count = serializers.IntegerField()
        image_name = serializers.CharField()
        file_name = serializers.CharField(required=False)
        function = serializers.CharField(required=False)
        params = serializers.ListField(required=False)
        type = serializers.ChoiceField(choices=JOB_TYPES)
        failure_action_grp = serializers.CharField(required=False)
        failure_action_ind = serializers.CharField(required=False)
        ctime = serializers.CharField(required=False)
        run_size = serializers.IntegerField(min_value=1, max_value=5)
        retry_count = serializers.IntegerField(min_value=0, max_value=3)
        group = GroupSerializer(read_only=True)
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    schedule = serializers.DateTimeField()
    tasks = TaskSerializer(many=True)
    ctime = serializers.DateTimeField()
    status = serializers.CharField()
    updated_by = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class JobCloneSerializer(serializers.Serializer):
    name = serializers.CharField()
    schedule = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
