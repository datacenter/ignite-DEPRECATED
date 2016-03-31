import glob
import os
import subprocess
import sys

from ignite.conf import DB_NAME, DB_USER, DB_PASSWORD, SYSLOG_PORT
from ignite.conf import IGNITE_IP, IGNITE_PORT, IGNITE_USER, IGNITE_PASSWORD
from ignite.conf import RMQ_USERNAME, RMQ_PASSWORD, RMQ_VHOST, CELERYD_USER,CELERYD_GROUP
from ignite.settings import UI_ROOT, MEDIA_ROOT, SCRIPT_PATH

CFG_FILE = os.path.join(SCRIPT_PATH, "bootstrap_config.py")
IMG_FILE = os.path.join(SCRIPT_PATH, "bootstrap_image.py")
POAP_FILE = os.path.join(SCRIPT_PATH, "poap.py")
JS_FILE = glob.glob(os.path.join(UI_ROOT,
                                 "scripts/utils/settings.*.js"))[0]
CELERYD_FILE = os.path.join(SCRIPT_PATH, "celeryd_config")


# sed command to replace IP & port in JS settings file
JS_SED_CMD = "sed -i 's/\(\"baseURL\"\s*\:\s*\"http\:\/\/\)\(.*\)\(\"\,\)/\\1'" \
             + IGNITE_IP + "':'" + IGNITE_PORT + "'\\3/' " + JS_FILE

# sed commands to replace ignite variables in poap.py
POAP_USER_CMD = "sed -i 's/^ignite_username = \".*\"/ignite_username = \"" \
                + IGNITE_USER + "\"/' " + POAP_FILE
POAP_PWD_CMD = "sed -i 's/^ignite_password = \".*\"/ignite_password = \"" \
               + IGNITE_PASSWORD + "\"/' " + POAP_FILE
POAP_IP_CMD = "sed -i 's/^ignite_hostname = \".*\"/ignite_hostname = \"" \
              + IGNITE_IP + "\"/' " + POAP_FILE
POAP_PORT_CMD = "sed -i 's/^ignite_port = \".*\"/ignite_port = \"" \
                + IGNITE_PORT + "\"/' " + POAP_FILE
POAP_MD5 = "python -c \"from scripts import ck_sum; ck_sum.get_ck_sum(\'" + POAP_FILE + "\')\""

# sed commands to replace syslog variables in bootstrap_config.py
CFG_IP_CMD = "sed -i 's/^SYSLOG_SERVER = \".*\"/SYSLOG_SERVER = \"" \
             + IGNITE_IP + "\"/' " + CFG_FILE
CFG_PORT_CMD = "sed -i 's/^SYSLOG_PORT = .*$/SYSLOG_PORT = " \
               + str(SYSLOG_PORT) + "/' " + CFG_FILE

# sed commands to replace syslog variables in bootstrap_image.py
IMG_IP_CMD = "sed -i 's/^SYSLOG_SERVER = \".*\"/SYSLOG_SERVER = \"" \
             + IGNITE_IP + "\"/' " + IMG_FILE
IMG_PORT_CMD = "sed -i 's/^SYSLOG_PORT = .*$/SYSLOG_PORT = " \
               + str(SYSLOG_PORT) + "/' " + IMG_FILE

# sed commands to replace celery variables in scripts/celeryd_config
CELERYD_USER_CMD = "sed -i 's/^CELERYD_USER=\".*\"/CELERYD_USER=\"" \
             + CELERYD_USER + "\"/' " + CELERYD_FILE
CELERYD_GROUP_CMD = "sed -i 's/^CELERYD_GROUP=\".*\"/CELERYD_GROUP=\"" \
             + CELERYD_GROUP + "\"/' " + CELERYD_FILE


CMD_LIST_SYSTEM_DEP = (
    ("Install Python 2.7 (may take a while)",
     "apt-get install python2.7"),
    ("Install Python dev (may take a while)",
     "apt-get install python-dev"),
    ("Install Python libpq dev (may take a while)",
     "apt-get install libpq-dev"),
    ("Install Python pip (may take a while)",
     "apt-get install python-pip"),
    ("Install Postgresql(may take a while)",
     "apt-get install postgresql-9.3 postgresql-common"),
    ("Install RabbitMQ (may take a while)",
     "apt-get install rabbitmq-server"),
)

CMD_LIST_PYTHON_DEP = (
    ("Install Python Packages (may take a while)",
     "pip install -r requirements.txt",),
)
CMD_LIST_SETUP = (
    ("Create Database (ignore error if database already exists)",
     "export PGPASSWORD=" + DB_PASSWORD + "\ncreatedb " + DB_NAME + " -U " + DB_USER,),
    ("Database Migrate",
     "python manage.py migrate",),
    ("Load user fixture",
     "python manage.py loaddata utils/fixtures/initial_data.json",),
    ("Load image profile fixture",
     "python manage.py loaddata image/fixtures/initial_data.json",),
    ("Load workflow fixtures",
     "python manage.py loaddata workflow/fixtures/initial_data.json",),
    ("Load switch fixtures",
     "python manage.py loaddata switch/fixtures/initial_data.json",),
    ("Javascript IP+Port Setting", JS_SED_CMD,),
    ("POAP User Setting", POAP_USER_CMD,),
    ("POAP Password Setting", POAP_PWD_CMD,),
    ("POAP IP Setting", POAP_IP_CMD,),
    ("POAP Port Setting", POAP_PORT_CMD,),
    ("POAP MD5", POAP_MD5,),
    ("Bootstrap Config Syslog IP Setting", CFG_IP_CMD,),
    ("Bootstrap Config Syslog Port Setting", CFG_PORT_CMD,),
    ("Bootstrap Image Syslog IP Setting", IMG_IP_CMD,),
    ("Bootstrap Image Syslog Port Setting", IMG_PORT_CMD,),
    ("RabbitMQ Username/Password Setting (ignore error if user already exists)",
     "rabbitmqctl add_user " + RMQ_USERNAME + " " + RMQ_PASSWORD,),
    ("RabbitMQ VHost Setting (ignore error if vhost already exists)",
     "rabbitmqctl add_vhost " + RMQ_VHOST,),
    ("RabbitMQ Permission Setting",
     "rabbitmqctl set_permissions -p " + RMQ_VHOST + " " + RMQ_USERNAME + " \".*\" \".*\" \".*\"",),
    ("Restart RabbitMQ Server",
     "service rabbitmq-server restart",),
    ("Setting Celery User", CELERYD_USER_CMD,),
    ("Setting Celery Group", CELERYD_GROUP_CMD,),
    ("Copying celeryd init",
     "cp scripts/celeryd /etc/init.d/celeryd",),
    ("Copying celeryd settings",
     "cp scripts/celeryd_config /etc/default/celeryd",),
    ("Starting celery worker",
     "/etc/init.d/celeryd restart",),
)

def exec_cmds(CMD_LIST, dep_type=""):
    for (name, cmd) in CMD_LIST:
        sys.stdout.write(name + " - ")
        sys.stdout.flush()

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        if not err:
            sys.stdout.write("[OK]\n")
            sys.stdout.flush()
        else:
            sys.stdout.write("[ERROR]\n")
            sys.stdout.write(err)
            sys.stdout.flush()
            # break

inp = raw_input("Have you modified Ignite settings in ignite/conf.py? [y/n] ")

if inp != "y" and inp != "Y":
    exit()

inp = raw_input("\nInstall system dependencies? [y/n] ")

if inp == "y" or inp == "Y":
    exec_cmds(CMD_LIST_SYSTEM_DEP)

inp = raw_input("\nInstall python dependencies? [y/n] ")
if inp == "y" or inp == "Y":
    exec_cmds(CMD_LIST_PYTHON_DEP)

sys.stdout.write("\nSetting up Ignite server\n")
sys.stdout.flush()

exec_cmds(CMD_LIST_SETUP)
