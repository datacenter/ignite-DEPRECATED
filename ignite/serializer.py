from rest_framework import serializers


class Neighbor(serializers.Serializer):
    local_port = serializers.CharField(required=True, max_length=100)
    remote_node = serializers.CharField(required=True, max_length=100)
    remote_port = serializers.CharField(required=True, max_length=100)

class POAPSerializer(serializers.Serializer):
    system_id = serializers.CharField(required=True, max_length=100)
    neighbor_list = Neighbor(required=True, many=True)
