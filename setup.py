import glob
import os
import subprocess

from ignite.conf import DB_NAME, DB_USER, DB_PASSWORD, SYSLOG_PORT
from ignite.conf import IGNITE_IP, IGNITE_PORT, IGNITE_USER, IGNITE_PASSWORD
from ignite.settings import UI_ROOT, MEDIA_ROOT, SCRIPT_PATH

CFG_FILE = os.path.join(SCRIPT_PATH, "bootstrap_config.py")
IMG_FILE = os.path.join(SCRIPT_PATH, "bootstrap_image.py")
POAP_FILE = os.path.join(SCRIPT_PATH, "poap.py")
JS_FILE = glob.glob(os.path.join(UI_ROOT,
                                 "scripts/utils/settings.*.js"))[0]

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


CMD_LIST = (
    ("Install Python Packages", "pip install -r requirements.txt",),
    ("Install Postgresql", "apt-get install postgresql",),
    ("Create Database (ignore error if database already exists)", "createdb " + DB_NAME + " -U " + DB_USER,),
    ("Database Migrate", "python manage.py migrate",),
    ("Load user fixture", "python manage.py loaddata utils/fixtures/initial_data.json",),
    ("Load image profile fixture", "python manage.py loaddata image/fixtures/initial_data.json",),
    ("Load workflow fixtures", "python manage.py loaddata workflow/fixtures/initial_data.json",),
    ("Javascript IP+Port Setting", JS_SED_CMD,),
    ("POAP User Setting", POAP_USER_CMD,),
    ("POAP Password Setting", POAP_PWD_CMD,),
    ("POAP IP Setting", POAP_IP_CMD,),
    ("POAP Port Setting", POAP_PORT_CMD,),
    ("Bootstrap Config Syslog IP Setting", CFG_IP_CMD,),
    ("Bootstrap Config Syslog Port Setting", CFG_PORT_CMD,),
    ("Bootstrap Image Syslog IP Setting", IMG_IP_CMD,),
    ("Bootstrap Image Syslog Port Setting", IMG_PORT_CMD,),
)


for (name, cmd) in CMD_LIST:
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if not proc.returncode:
        print "[OK] -", name
    else:
        print "[ERROR] -", name
        print err
        # break
