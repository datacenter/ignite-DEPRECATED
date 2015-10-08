INVALID = -1
LOG_SEARCH_COL = 3
HOST_NAME_REGEX = "(host)([1-9]+[0-9]*)"
INSTANCE_REGEX = "_[1-9][0-9]*_"


#Topology JSON

SWITCH_NAME = "name"
SWITCH_TYPE = "type"
CORE_LIST   = "core_list"
LEAF_LIST   = "leaf_list"
SPINE_LIST  = "spine_list"
LINK_LIST   = "link_list"
SWITCH_1    = "switch_1"
SWITCH_2    = "switch_2"
PORTLIST_1  = "port_list_1"
PORTLIST_2  = "port_list_2"
LINK_TYPE   = "link_type"

#CDP JSON
NEIGHBOR_LIST  = "neighbor_list"
REMOTE_NODE    = "remote_node"
REMOTE_PORT    = "remote_port"
LOCAL_PORT     = "local_port"

#Fabric JSON
CONFIGURATION_ID = "configuration_id"

#VPC Peer Detail Response
VPC_PEER_SWITCH = "vpc_peer_switches"
VPC_SWITCH_LOCALPORT = "vpc_switch_localport"
VPC_PEER_CDP_STATUS = "vpc_peer_cdp_status"
VPC_DETAIL_RESPONSE = {VPC_PEER_SWITCH:"",VPC_SWITCH_LOCALPORT:[]}

MATCH_TYPE_NEIGHBOUR = 'Neighbour'
MATCH_TYPE_SYSTEM_ID = 'System_ID'

FABRIC_MATCH_RESPONSE = \
{"CFG_ID":INVALID,"FABRIC_ID":INVALID,"SWITCH_ID":"","DISCOVERYRULE_ID": INVALID, \
  "MATCH_TYPE": "", "REPLICA_NUM":INVALID}

