RADIUS = "radius"
TACACS = "tacacs+"
SERVER_CHOICE = [RADIUS, TACACS]

SERVER = 'server_ip'
PORT = 'port'
SECRET = 'secret'
PROTOCOL = 'protocol'

USERNAME = "username"
PASSWORD = "password"
EMAIL = "email"
IS_SUPERUSER = "is_superuser"

ADMIN = "admin"


# Backup constants
TAR_FORMAT = ".tar.gz"
SQL_FORMAT = ".sql"
FILE_LIST = ["configlets", "features", "repo"]
CONF_FILE = "ignite/conf.py"
MEDIA = "media"
BACKUP = "backup"

# change of this contant needst to change url also
FILE_TIME_FORMAT = "%Y_%m_%d_%H%M%S"

BACKUP_SUCCESS_MSG = "Backup is successful "

# backup error msgs
ERR_BACKUP_NOT_FOUND = "Backup not found with file name "
ERR_FAILED_TO_BACKUP_DB = "Failed to backup db"
ERR_FAILED_TO_REMOVE = "Failed to remove file"
ERR_USER_ADMIN = "Admin can't be deleted"
ERR_NOT_LIST = "Expecting a list"
ERR_EMPTY_LIST = "List is empty, Excepting list of filenames"
