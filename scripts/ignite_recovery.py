#!/usr/bin/python

import os
import psycopg2
import sys
import subprocess
import shutil
import tarfile

BASE_DIR = os.path.join(os.getcwd(), "..")
sys.path.append(os.path.join(BASE_DIR))

from administration.constants import *
from ignite.conf import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from ignite.settings import MEDIA_ROOT, BASE_DIR


def execute_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if not proc.returncode:
        print "[OK] -", cmd
        return True
    else:
        print "[ERROR] -", cmd
        print err
        return False


def db_recover(f):
    cmd = "createdb -U %s %s" %(DB_USER, DB_NAME)
    status = execute_cmd(cmd)

    filename = os.path.join(os.getcwd(), "..", MEDIA, f)
    command = 'export PGPASSWORD=%s\npsql -U %s -d %s  -f %s' % (DB_PASSWORD, DB_USER, DB_NAME, filename)
    status = execute_cmd(command)
    if not status:
        exit()
    
    command = "rm " + filename
    status = execute_cmd(command)
    if not status:
        exit()


def restore(filename):
    if os.path.exists(filename):
        tar = tarfile.open(filename)
        tar.extractall(path=os.path.join(os.getcwd(), ".."))
        tar.close()

        for f in os.listdir(os.path.join(os.getcwd(), "..", MEDIA)):
            if f.endswith(SQL_FORMAT):
                db_recover(f)

        return "successfull"

    return "file not found/incorrect file name"


if __name__ == "__main__":
    filename = sys.argv[1]
    status = restore(filename)
    print status
