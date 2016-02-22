#File extensions
CFG_FILE_EXT = ".cfg"
YAML_FILE_EXT = ".yml"

#Keys for server response
ACCESS_METHOD = "access_method"
SERVER_IP = "ignite_ip"
SERVER_USER = "ignite_user"
SERVER_PASSWORD = "ignite_password"
STATUS = "status"
FILE = "yaml_file"
ERR_MSG = "err_msg"
YAML_PATH = 'yaml_lib'

#Swich Boot Status
BOOT_PROGRESS = "In progress"
BOOT_SUCCESS = "Success"
BOOT_FAIL = "Failed"
NOT_BOOTED = 'Not Booted'

#logs
LOG_SEARCH_COL = 3
SYSLOG_PATH = '/var/log/syslog*'

#Error Messages
ERR_NO_RESPONSE = "No match found for serial number or neighbor list"
ERR_CONFIG_NOT_BUILD = "Config not build for switch"
ERR_FAILED_TO_READ_SYSLOGS = 'Failed to read syslogs'
ERR_SWITCH_NOT_BOOTED = "Switch has not yet booted"
ERR_SERIAL_NOT_FOUND = "Serial number not found"
ERR_DISOVERY_RULE_EXIST = "Discovery rule for switch does not exist"
ERR_SWITCH_BOOT_IN_PROGRESS = "Can not update. Booting is in progress"
ERR_CREATE_BOOT_STATUS = "Failed to create boot status of switch without build time"
ERR_SERIAL_NUM_MISMATCH = "Serial number not found for status update"
ERR_SWITCH_IN_USE_JOB_SCHEDULE = "Switch is busy in Job scheduling. Can not be updated"

#RMA Match
SWITCH = 'switch'
RULE = 'rule'

#RMA Case
BOOT_DETAIL = 'boot_detail'
BOOT_STATUS = 'boot_status'
BOOT_TIME = 'boot_time'
DISCOVERY_RULE = 'discovery_rule'
ERROR = 'error'
FABRIC_NAME = 'fabric_name'
MATCH_TYPE = 'match_type'
RMA_MATCH = [SWITCH, RULE]
NEIGHBOR = 'Neighbor'
NEW_SERIAL_NUM = "new_serial_num"
OLD_SERIAL_NUM = "old_serial_num"
RULE_ID = 'rule_id'
SWITCH_NAME = 'switch_name'
TOPOLOGY = 'topology'
