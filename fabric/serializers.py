from rest_framework import serializers

from constants import LINK_TYPES, MATCH_TYPES, TIER_NAMES, CONFIG_LIST
from constants import FAB_CLONE_NAME
from models import Topology


NUM_LINKS_MIN = 1
NUM_LINKS_MAX = 4
COUNT_MIN = 0
COUNT_MAX = 128


class NameSerializer(serializers.Serializer):

    name = serializers.CharField()


class TopologyBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    model_name = serializers.CharField()
    submit = serializers.BooleanField()
    updated = serializers.DateTimeField()
    updated_by = serializers.CharField()


class DefaultLinkSerializer(serializers.Serializer):

    src_tier = serializers.ChoiceField(TIER_NAMES)
    dst_tier = serializers.ChoiceField(TIER_NAMES)
    link_type = serializers.ChoiceField(LINK_TYPES)
    num_links = serializers.IntegerField(min_value=NUM_LINKS_MIN,
                                         max_value=NUM_LINKS_MAX)


class TopologyPostDefaultsSerializer(serializers.Serializer):

    class TopologyPostDefaultSwitchSerializer(serializers.Serializer):

        tier = serializers.ChoiceField(TIER_NAMES)
        model = serializers.IntegerField()
        image_profile = serializers.IntegerField()

    switches = TopologyPostDefaultSwitchSerializer(many=True)
    links = DefaultLinkSerializer(many=True)


class TopologyPostSerializer(serializers.Serializer):

    name = serializers.CharField()
    model_name = serializers.CharField()
    defaults = TopologyPostDefaultsSerializer()


class TopologyDefaultsSerializer(serializers.Serializer):

    class TopologyDefaultSwitchSerializer(serializers.Serializer):

        tier = serializers.ChoiceField(TIER_NAMES)
        model = serializers.PrimaryKeyRelatedField(read_only=True)
        image_profile = serializers.PrimaryKeyRelatedField(read_only=True)

    switches = TopologyDefaultSwitchSerializer(many=True)
    links = DefaultLinkSerializer(many=True)


class LinkSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    src_switch = serializers.PrimaryKeyRelatedField(read_only=True)
    dst_switch = serializers.PrimaryKeyRelatedField(read_only=True)
    link_type = serializers.ChoiceField(LINK_TYPES)
    num_links = serializers.IntegerField(min_value=NUM_LINKS_MIN,
                                         max_value=NUM_LINKS_MAX)
    src_ports = serializers.CharField()
    dst_ports = serializers.CharField()


class TopologySerializer(serializers.Serializer):

    class TopologySwitchSerializer(serializers.Serializer):

        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField()
        tier = serializers.ChoiceField(TIER_NAMES)
        model = serializers.PrimaryKeyRelatedField(read_only=True)
        image_profile = serializers.PrimaryKeyRelatedField(read_only=True)

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    model_name = serializers.CharField()
    submit = serializers.BooleanField()
    defaults = TopologyDefaultsSerializer()
    switches = TopologySwitchSerializer(many=True)
    links = LinkSerializer(many=True)


class SwitchPostSerializer(serializers.Serializer):

    class TierCountSerializer(serializers.Serializer):

        tier = serializers.ChoiceField(TIER_NAMES)
        count = serializers.IntegerField(min_value=COUNT_MIN,
                                         max_value=COUNT_MAX)

    switches = TierCountSerializer(many=True)


class TopologySwitchPutSerializer(serializers.Serializer):

    model = serializers.IntegerField()
    image_profile = serializers.IntegerField(allow_null=True)


class LinkPostSerializer(serializers.Serializer):

    src_switch = serializers.IntegerField()
    dst_switch = serializers.IntegerField()
    link_type = serializers.ChoiceField(LINK_TYPES)
    num_links = serializers.IntegerField(min_value=NUM_LINKS_MIN,
                                         max_value=NUM_LINKS_MAX)


class LinkPutSerializer(serializers.Serializer):

    link_type = serializers.ChoiceField(LINK_TYPES)
    num_links = serializers.IntegerField(min_value=NUM_LINKS_MIN,
                                         max_value=NUM_LINKS_MAX)
    src_ports = serializers.CharField()
    dst_ports = serializers.CharField()


class FabricBriefSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    model_name = serializers.CharField()
    submit = serializers.BooleanField()
    is_discovered = serializers.BooleanField()
    build_time = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField()
    updated_by = serializers.CharField()
    site = serializers.CharField()


class FabricProfilesSerializer(serializers.Serializer):

    tier = serializers.ChoiceField(TIER_NAMES)
    config_profile = serializers.IntegerField(allow_null=True)
    feature_profile = serializers.IntegerField(allow_null=True)
    workflow = serializers.IntegerField(allow_null=True)


class FabricPostSerializer(serializers.Serializer):

    name = serializers.CharField()
    topology = serializers.IntegerField()
    config_profile = serializers.IntegerField(allow_null=True)
    feature_profile = serializers.IntegerField(allow_null=True)
    switches = FabricProfilesSerializer(many=True)


class FabricDefaultsSerializer(serializers.Serializer):

    class FabricDefaultSwitchSerializer(serializers.Serializer):

        tier = serializers.ChoiceField(TIER_NAMES)
        model = serializers.PrimaryKeyRelatedField(read_only=True)
        image_profile = serializers.PrimaryKeyRelatedField(read_only=True)
        config_profile = serializers.PrimaryKeyRelatedField(read_only=True)
        feature_profile = serializers.PrimaryKeyRelatedField(read_only=True)
        workflow = serializers.PrimaryKeyRelatedField(read_only=True)

    switches = FabricDefaultSwitchSerializer(many=True)
    links = DefaultLinkSerializer(many=True)


class FabricSwitchPutSerializer(serializers.Serializer):

    name = serializers.CharField()
    serial_num = serializers.CharField(allow_blank=True)
    model = serializers.IntegerField()
    image_profile = serializers.IntegerField(allow_null=True)
    config_profile = serializers.IntegerField(allow_null=True)
    feature_profile = serializers.IntegerField(allow_null=True)
    workflow = serializers.IntegerField(allow_null=True)
    config_type = serializers.ChoiceField(CONFIG_LIST)


class FabricProfilesPutSerializer(serializers.Serializer):

    config_profile = serializers.IntegerField(allow_null=True)
    feature_profile = serializers.IntegerField(allow_null=True)
    profiles = FabricProfilesSerializer(many=True)


class CloneTopoSerializer(serializers.Serializer):
    name = serializers.CharField()


class CloneFabricSerializer(serializers.Serializer):
    name = serializers.CharField()
    name_operation = serializers.ChoiceField(FAB_CLONE_NAME)


class DiscoveryPostSerializer(serializers.Serializer):

    class AuthDetailsSerializer(serializers.Serializer):

        username = serializers.CharField()
        password = serializers.CharField()

    class BlockSerializer(serializers.Serializer):
        start = serializers.CharField()
        end = serializers.CharField()

    auth_details = AuthDetailsSerializer()
    leaf_ip = serializers.CharField()
    spine_ip = serializers.CharField()
    ip_range = BlockSerializer(many=True)

class DiscoverySaveSerializer(serializers.Serializer):
    
    name = serializers.CharField()


class FabricSerializer(serializers.Serializer):

    class FabricSwitchSerializer(serializers.Serializer):

        class SwitchBootDetailSerializer(serializers.Serializer):

            boot_status = serializers.CharField()
            match_type = serializers.ChoiceField(MATCH_TYPES)
            boot_time = serializers.DateTimeField()

        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField()
        tier = serializers.ChoiceField(TIER_NAMES)
        serial_num = serializers.CharField()
        model = serializers.PrimaryKeyRelatedField(read_only=True)
        image_profile = serializers.PrimaryKeyRelatedField(read_only=True)
        config_profile = serializers.PrimaryKeyRelatedField(read_only=True)
        feature_profile = serializers.PrimaryKeyRelatedField(read_only=True)
        workflow = serializers.PrimaryKeyRelatedField(read_only=True)
        config_type = serializers.ChoiceField(CONFIG_LIST)
        boot_detail = SwitchBootDetailSerializer()

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    model_name = serializers.CharField()
    submit = serializers.BooleanField()
    is_discovered = serializers.BooleanField()
    is_saved = serializers.BooleanField()
    build_time = serializers.DateTimeField(read_only=True)
    config_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    feature_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.CharField()
    defaults = FabricDefaultsSerializer()
    switches = FabricSwitchSerializer(many=True)
    links = LinkSerializer(many=True)
    maintenance_group_count  = serializers.IntegerField(read_only=True)

class DiscoveredFabricSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    model_name = serializers.CharField()
    submit = serializers.BooleanField()
    build_time = serializers.DateTimeField(read_only=True)
    config_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    feature_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.CharField()


class SwitchConfigSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SwitchConfigListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    version = serializers.IntegerField()
    last_updated = serializers.DateTimeField(read_only=True)
