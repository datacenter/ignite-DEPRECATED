# globals
CONFIGLET_ID = "configlet_id"
CONFIGLETINDEX_ID = "configletindex_id"
CONSTRUCT_LIST = "construct_list"
FALSE = "false"
FILE = "file"
GROUP = "group"
NAME = "name"
SUBMIT = "submit"
TRUE = "true"
CONSTRUCT_TYPE = "type"
VERSION = "version"
NEW_VERSION = "new_version"

PARAM_LIST = 'param_list'
PARAM_NAME = 'param_name'
PARAM_TYPE = 'param_type'
PARAM_VALUE = 'param_value'

#Regural expressions for parameters identifications
PARAM_EXP_CONFIGLET = '\$\$[0-9a-zA-Z_]+\$\$'
PARAM_EXP_SCRIPT = '__[0-9a-zA-Z_]+__'

#parameter delimeter
PARAM_IDENTIFIER_SCRIPT = "__"
PARAM_IDENTIFIER_CONFIGLET = "$$"

#Construct type choices
SCRIPT = 'script'
CONFIGLET = 'configlet'

CONSTRUCT_TYPE_OPTIONS = [SCRIPT, CONFIGLET]

# param types
FIXED = "Fixed"
INSTANCE = "Instance"
POOL = "Pool"
VALUE = "Value"
EVAL = "Eval"

PARAM_TYPES = [FIXED, INSTANCE, POOL, VALUE, EVAL]

# error messages
ERR_CFG_IN_USE = "Configlet is in use"
ERR_EVAL_SYNTAX = "Syntax error in eval string"
ERR_IN_PROCESSING_SCRIPT = "Failed to process script"
ERR_PROF_IN_USE = "Profile is in use"
ERR_VALUE_NOT_FOUND = "Value not found for parameter"
ERR_PROF_IS_EMPTY = "No configlet is added"
ERR_CONFIGLET_FILE_NOT_FOUND = "Configlet not found"
ERR_CAN_NOT_DELETE_DEFAULT_CONFIG = "Deletion of default config profile is not allowed"
ERR_CAN_NOT_EDIT_DEFAULT_CONFIG = "Can not edit default config profile"
ERR_CHANGE_IN_PARAMS = "Parameters are changed"

# Instance dependent params
HOST_NAME = 'HOST_NAME'
VPC_PEER_SRC = 'VPC_PEER_SRC'
VPC_PEER_DST = 'VPC_PEER_DST'
VPC_PEER_PORTS = 'VPC_PEER_PORTS'
UPLINK_PORTS = 'UPLINK_PORTS'
DOWNLINK_PORTS = 'DOWNLINK_PORTS'

# Instance param type valid choices
INSTANCE_PARAM_VALUE = [HOST_NAME, VPC_PEER_SRC, VPC_PEER_DST, VPC_PEER_PORTS,
                        UPLINK_PORTS, DOWNLINK_PORTS]
