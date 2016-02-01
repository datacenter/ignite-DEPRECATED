# choices
CHOICES = ['contain', 'no_contain', 'match', 'no_match',  'any']
MATCH_CHOICES = ['all', 'any', 'All', 'Any', 'serial_num', 'ALL', 'ANY']

# constants for discovery rules
SERIAL_NUM = 'serial_num'
MATCH = 'match'
NO_MATCH = 'no_match'
NAME = 'name'
PRIORITY = 'priority'
CONFIG = 'config'
WORKFLOW = 'workflow'
IMAGE = 'image'
SUBRULES = 'subrules'
NEIGH_LIST = 'neighbor_list'
RN_CONDITION = 'rn_condition'
RP_CONDITION = 'rp_condition'
LP_CONDITION = 'lp_condition'
NONE = 'none'
RN_STR = 'rn_string'
RP_STR = 'rp_string'
LP_STR = 'lp_string'
REMOTE_NODE = 'remote_node'
REMOTE_PORT = 'remote_port'
LOCAL_PORT = 'local_port'
ALL = 'all'
ANY = 'any'
CONTAIN = 'contain'
NO_CONTAIN = 'no_contain'

# error constants
ERR_SERIAL_REPEATED = 'Serial number is repeated'
ERR_SERIAL_EXISTS_DISRULES = ' serial number is assigned in discovery rule '
ERR_SERIAL_EXISTS_FABRIC = ' serial number is assigned in fabric'
