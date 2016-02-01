# globals
ALL = "all"
NAME = "name"

# port group
NUM_PORTS = "num_ports"
PORT_GROUPS = "port_groups"
ROLE = "role"
SPEED = "speed"
TRANSCEIVER = "transceiver"

# port roles
BOTH = "Both"
DOWNLINK = "Downlink"
UPLINK = "Uplink"

PORT_ROLES = [BOTH, DOWNLINK, UPLINK]
PORT_SPEEDS = ["1/10G", "40G", "100G"]
TRANSCEIVERS = ["GBASE-T", "SFP+", "QSFP+", "QSFP28", "CFP2"]

# line card
LC_DATA = "lc_data"
LC_TYPE = "lc_type"

# line card types
LINECARD = "Linecard"
MODULE = "Module"

LC_TYPES = [MODULE, LINECARD]

# switch
BASE_MODEL = "base_model"
LC_ID = "lc_id"
MODULE_ID = "module_id"
NUM_SLOTS = "num_slots"
SLOTS = "slots"
SLOT_NUM = "slot_num"
SWITCH_DATA = "switch_data"
SWITCH_TYPE = "switch_type"
TIERS = "tiers"

# switch types
CHASSIS = "Chassis"
FIXED = "Fixed"

SWITCH_TYPES = [FIXED, CHASSIS]

# error messages
ERR_INV_SW_TYPE = "Invalid switch type"
ERR_LC_IN_USE = "Line card is in use"
ERR_SW_IN_USE = "Switch model is in use"
ERR_SW_SLOT_IN_USE = "Slot_num is in use"
