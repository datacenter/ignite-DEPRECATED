#Access protocols
ACCESS_PROTOCOLS = ["sftp", "tftp", "scp", "http"]

#task keys
NAME = "name"
HANDLER = "handler"
FUNCTION = "function"
DESCRIPTION = "desc"
PARAMETERS = "parameters"
LOCATION = "location"
LOC_ACCESS_PROTO = "location_access_protocol"
LOC_SERVER_IP = "location_server_ip"
LOC_SERVER_USER = "location_server_user"
LOC_SERVER_PASSWORD = "location_server_password"

#Workflow keys
SUBMIT = "submit"
TASK_LIST = "task_list"
TASK_ID = "task_id"

#Workflow YAML Keys
TASK = 'task'

#Errors
ERR_TASK_IN_USE = "Task is in use"
ERR_TASK_NOT_EDITABLE = "Task is not editable"
ERR_WF_NOT_EDITABLE = "Workflow is not editable"

#Parameters for bootstrap tasks
PROTOCOL = "protocol"
HOSTNAME = "hostname"
FILE_SRC = "file_src"
FILE_DST = "file_dst"
USERNAME = "username"
PASSWORD = "password"

#Default workflow
BOOTSTRAP_WORKFLOW_ID = 1

#Default tasks
BOOTSTRAP_CONFIG_ID = 1
BOOTSTRAP_IMAGE_ID = 2

#Bootstrap scripts name
BOOTSTRAP_CONF_SCRIPT = "bootstrap_config.py"
BOOTSTRAP_IMAGE_SCRIPT = "bootstrap_image.py"
