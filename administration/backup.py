from datetime import datetime
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import mimetypes
import os
import psycopg2
import platform
import subprocess
import tarfile

from constants import *
from ignite.conf import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from ignite.settings import MEDIA_ROOT, BASE_DIR
from models import AAAServer, AAAUser
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def execute_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if not proc.returncode:
        logger.debug("[OK] - " + cmd)
        return True
    else:
        logger.error("[ERROR] - " + cmd)
        logger.error(str(err))
        return False


def db_dump(filename):
    OS_DISTRIBUTION_NAME = platform.linux_distribution()[0]
    logger.debug("db backup file name '%s'" % filename)

    if OS_DISTRIBUTION_NAME == 'Ubuntu':
        command = 'export PGPASSWORD=%s\npg_dump %s -U %s --file="%s" -h localhost' % (DB_PASSWORD, DB_NAME, DB_USER, filename)

    elif OS_DISTRIBUTION_NAME == 'CentOS Linux':
        PATH_TO_PG_DUMP = '/usr/pgsql-9.3/bin/'
	PG_COMMAND = PATH_TO_PG_DUMP + 'pg_dump %s -U %s --file="%s" -h localhost' % (DB_NAME, DB_USER, filename)
	command = 'export PGPASSWORD=%s\n' % (DB_PASSWORD) + PG_COMMAND
    else:
        raise IgniteException(ERR_UNKNOWN_OS_TYPE)

    status = execute_cmd(command)
    if not status:
        raise IgniteException(ERR_FAILED_TO_BACKUP_DB)

    logger.debug("db backup is done")


def create_backup():
    cwd = os.getcwd()
    os.chdir(BASE_DIR)
    current_date = datetime.utcnow().strftime(FILE_TIME_FORMAT)
    filename = os.path.join(MEDIA_ROOT, current_date + SQL_FORMAT)
    backup_name = "Ignite_" + current_date + TAR_FORMAT
    tar_name = os.path.join(MEDIA_ROOT, BACKUP, backup_name)

    db_dump(filename)

    file_obj = tarfile.open(tar_name, "w:gz")
    logger.debug("cwd = " + os.getcwd())
    for name in FILE_LIST:
        file_obj.add(MEDIA + "/" + name)

    file_obj.add(MEDIA + "/" + current_date + SQL_FORMAT)
    file_obj.close()

    try:
        os.remove(filename)
    except:
        delete_backup([current_date + TAR_FORMAT])
        raise IgniteException(ERR_FAILED_TO_REMOVE + filename)

    resp = {}
    resp["status"] = "success"
    resp["filename"] = backup_name
    os.chdir(cwd)
    return resp


def get_list():
    cwd = os.getcwd()
    os.chdir(BASE_DIR)
    names = os.listdir(os.path.join(MEDIA_ROOT, BACKUP))
    tar_list = []
    for name in names:
        if name.endswith(TAR_FORMAT):
            tar_list.append(name)
    path = MEDIA + "/" + BACKUP + "/"
    tar_list.sort(key=lambda x: os.path.getmtime(path+x))
    tar_list.reverse()
    os.chdir(cwd)
    return tar_list


def download_backup(fn):
    cwd = os.getcwd()
    os.chdir(BASE_DIR)
    fn = fn + TAR_FORMAT
    filename = MEDIA + "/" + BACKUP + "/" + fn
    if os.path.isfile(filename):
        if fn.endswith(TAR_FORMAT):
            wrapper = FileWrapper(file(filename))
            response = HttpResponse(wrapper)
            format_name = os.path.basename(filename)
            filesize = os.path.getsize(filename)
            content_disposition = 'attachment; filename="%s"' % (format_name)
            response['Content-Disposition'] = content_disposition
            content_type = mimetypes.guess_type(filename)[0]
            response['Content-Type'] = content_type
            response['Content-Length'] = str(filesize)
            return response
    os.chdir(cwd)
    raise IgniteException(ERR_BACKUP_NOT_FOUND + fn)


def delete_backup(data):
    if not type(data) is list:
        raise IgniteException(ERR_NOT_LIST)

    if not data:
        raise IgniteException(ERR_EMPTY_LIST)

    for name in data:
        filename = os.path.join(MEDIA_ROOT, BACKUP, name)
        if os.path.isfile(filename):
            if filename.endswith(TAR_FORMAT):
                status = os.remove(filename)
