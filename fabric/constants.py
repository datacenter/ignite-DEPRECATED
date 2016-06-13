# globals
CONFIG_PROFILE = "config_profile"
COUNT = "count"
DEFAULT = "DEFAULT"
DEFAULTS = "defaults"
DISCOVERY = "Discovery"
DST_PORTS = "dst_ports"
DST_SWITCH = "dst_switch"
DST_TIER = "dst_tier"
FALSE = "false"
FEATURE_PROFILE = "feature_profile"
ID = "id"
IMAGE_PROFILE = "image_profile"
LINKS = "links"
LINK_TYPE = "link_type"
MODEL = "model"
MODEL_NAME = "model_name"
NAME = "name"
NEIGHBOR = "Neighbor"
NUM_LINKS = "num_links"
PARAM_LIST = "param_list"
PROFILES = "profiles"
SERIAL_NUM = "serial_num"
SERIAL_NUMBER = "Serial Number"
SRC_PORTS = "src_ports"
SRC_SWITCH = "src_switch"
SRC_TIER = "src_tier"
SWITCHES = "switches"
TIER = "tier"
TOPOLOGY = "topology"
TRUE = "true"
WORKFLOW = "workflow"

# topology models
LEAF_SPINE = "Leaf-Spine"

TOPOLOGY_MODELS = [LEAF_SPINE]

# tiers
BORDER = "Border"
CORE = "Core"
LEAF = "Leaf"
SPINE = "Spine"

TIER_NAMES = [BORDER, CORE, LEAF, SPINE]

# max spines and leafs
MAX_SPINES = 8
MAX_LEAFS = 128
MAX_CORES = 8
MAX_BORDERS = 8

# link types
PHYSICAL = "Physical"
PORT_CHANNEL = "Port-Channel"
VPC_MEMBER = "VPC-Member"
VPC_PEER = "VPC-Peer"

LINK_TYPES = [PHYSICAL, PORT_CHANNEL, VPC_MEMBER, VPC_PEER]

# CDP request
LOCAL_PORT = 'local_port'
NEIGHBOR_LIST = 'neighbor_list'
REMOTE_NODE = 'remote_node'
REMOTE_PORT = 'remote_port'

# Match types
MATCH_TYPES = [SERIAL_NUMBER, NEIGHBOR, DISCOVERY]

# fabric clone name
REPLACE = "replace"
PREPEND = "prepend"
FAB_CLONE_NAME = [REPLACE, PREPEND]
NAME_OPERATION = "name_operation"

# fabric discovery
IP_RANGE = 'ip_range'
START = 'start'
END = 'end'
SPINE_IP = 'spine_ip'
LEAF_IP = 'leaf_ip'

#running config
POAP_CONFIG = 'POAP_CONFIG'
RUNNING_CONFIG = 'RUNNING_CONFIG'
CONFIG_TYPE = 'config_type'
CONFIG_LIST = [POAP_CONFIG, RUNNING_CONFIG]

# error messages
ERR_BUILD_WITHOUT_SUBMIT = "Submit the fabric before build config"
ERR_CANT_DEL_BOOTED_FABRIC = "Cannot delete a fabric that is already booted"
ERR_CANT_DEL_BOOTED_SWITCH = "Cannot delete a switch that is already booted"
ERR_CANT_DEL_PROGRESS_SWITCH = "Booting in progress, can not delete"
ERR_CLONE_FABRIC = "Cloning is not possible, switch name repeated"
ERR_FABRIC_SWITCH_DIFFERENT = "Switch is not part of the given fabric"
ERR_INV_PORTS = "Ports are either in use or not of right type"
ERR_INV_PORT_COUNT = "Port count does not match # of links"
ERR_INV_TOP_MODEL = "Invalid topology model name"
ERR_LS_LINK_DEL_NOT_ALLOWED = "Leaf-Spine link delete not allowed"
ERR_MGMT_IP_NOT_DETERMINED = "Failed to get the Mgmt IP"
ERR_NO_DOWNLINK_PORTS = "No Downlink ports found for switch"
ERR_NO_NAME_CHANGE = "Name, Model and Serial_num changes are  not allowed after fabric switch has booted"
ERR_NO_UPLINK_PORTS = "No Uplink ports found for switch"
ERR_NO_VPC_PEER_PORTS = "No VPC peer ports found for switch"
ERR_NO_VPC_PEER_SWITCH = "No VPC peer switch found"
ERR_NOT_ENOUGH_PORTS = "Not enough ports available on switch to add link(s)"
ERR_PEER_MGMT_IP_NOT_DETERMINED = "Failed to determine the peer switch Mgmt IP"
ERR_RUN_CONFIG_NOT_AVAL = "Switch Running config is not available"
ERR_REQUEST_WITHOUT_SUBMIT = "Submit the fabric first before POAP request"
ERR_SERIAL_NUM_IN_USE = "Serial number is already assigned"
ERR_SW_IN_USE = "Switch is in use"
ERR_SW_NAME_IN_USE = "Switch name is already in use"
ERR_TIER_NOT_RECOGNIZED = "Not a valid tier for topology"
ERR_VALUE_NOT_FOUND = "Failed to get value for parameter"
ERR_SAME_SPINE_LEAF_IP = "Invalid: Spine and Leaf IP can not be same"
ERR_SWITCH_CONFIG_FAILED = "Failed to pull switch config"
ERR_SWITCH_CONFIG_NOT_AVAILABLE = "No config available"
ERR_CAN_NOT_ASSIGN_UNKOWN_MODEL = "Can not assign unknown model to the switch"
ERR_UNABLE_TO_GET_SPINE_SWITCH_INFO = "Unable to get Spine switch info"
ERR_UNABLE_TO_GET_LEAF_SWITCH_INFO = "Unable to get Leaf switch info"
ERR_SPINE_EXCEEDED_MAX_LIMIT = "Number of Spines can not exceed max limit of 8"
ERR_LEAF_EXCEEDED_MAX_LIMIT = "number of Leafs can not exceed max limit of 128"
ERR_CORE_EXCEEDED_MAX_LIMIT = "number of Cores can not exceed max limit of 8"
ERR_BORDER_EXCEEDED_MAX_LIMIT = "number of Borders can not exceed max limit of 8"
ERR_CAN_NOT_RESET = "Can not reset the switch in Boot state : "
ERR_SWITCH_NOT_BOOTED = "Switch is not booted. Can not reset"
