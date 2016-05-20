# Ignite Configuration File

# Database Parameters
DB_NAME = "ignite"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = ""

# Ignite server access details
IGNITE_IP = "127.0.0.1"
IGNITE_PORT = "8000"
IGNITE_USER = "ignite"
IGNITE_PASSWORD = "ignite"

# logs path for switch specific logs file in Ignite server
REMOTE_SYSLOG_PATH = "/var/log/remote/ignite/system-"

#ACCESS_METHODS
#tftp : trivial file transfer protocol
#scp : secure copy
#sftp : ssh file transfer protcol
#http : hypertext transfer protocol
ACCESS_PROTOCOL = "scp"

# syslog port
SYSLOG_PORT = 514

# number of lines to display in logs
LOG_LINE_COUNT = 500

# log file name
SYSLOG_PATH = "/var/log/syslog*"

# RabbitMQ Settings
RMQ_USERNAME = "admin"
RMQ_PASSWORD = "admin"
RMQ_VHOST = "vhost"

#Celery Daemon Settings
CELERYD_USER = "user"
CELERYD_GROUP = "user"

# Project directory (will be prefixed to BASE_DIR)
#Do not change this parameter is server is hosted inside apache2 and is placed in /var/www/ folder.
PROJECT_DIR = "ignite"

