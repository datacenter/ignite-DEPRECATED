#!/bin/env python

from cli import *
import imp
import json
import multiprocessing
import os
import signal
import socket
import sys
import time
import urllib2


#Ignite server access details - fill in from ignite/config.py
ignite_username = "ignite"
ignite_password = "ignite"
ignite_hostname = "127.0.0.1"
ignite_port = "8000"
vrf = "management"

#non editable
IGNITE_REST_API_CDP = '/api/bootstrap'
IGNITE_URL_CDP = "http://%s:%s%s" % (ignite_hostname, ignite_port, IGNITE_REST_API_CDP)
IGNITE_REST_API_STATUS = '/api/bootstrap/status'
IGNITE_URL_STATUS = "http://%s:%s%s" % (ignite_hostname, ignite_port, IGNITE_REST_API_STATUS)
REQUEST_PARAMS = {'Content-Type': 'application/json'}


#Ignite Response parameters
RESP_USERNAME = 'ignite_user'
RESP_PASSWORD = 'ignite_password'
RESP_HOSTNAME = 'ignite_ip'
RESP_PORT = ''
RESP_FILE_SRC = 'yaml_file'
RESP_STATUS = 'status'
RESP_ERR = 'err_msg'
RESP_ACCESS_METHOD = 'access_method'
RESP_YAML_LIB_PATH = 'yaml_lib'

#Task parameters
TASK_NAME = 'name'
TASK_FUNCTION = 'function'
TASK_LOC = 'location'
TASK_LIST = 'task'
TASK_PARAMETER = 'parameters'
TASK_HANDLER = 'handler'
#Added by script
TASK_DST = 'task_dst'
MODULE_NAME = 'module_name'
PROC_HANDLE = 'proc_handle'

#Location Parameters
#AUTH = 'authentication'
HOSTNAME = 'hostname'
ACCESS_PROTOCOL = 'protocol'
USERNAME = 'username'
PASSWORD = 'password'
LOCATION_LIST = 'location'

#Arguments needed for get_file/do_copy:
file_name = ''
file_loc = ''
file_src = ''
hostname = ''
port = ''
access_protocol = ''
username = ''
password = ''

#Access protocols
PROTO_SCP = 'scp'
PROTO_TFTP = 'tftp'
PROTO_SFTP = 'sftp'
PROTO_HTTP = 'http'

#CDP/Status Json
SERIAL_NUM = 'serial_num'
NEIGHBOR_LIST = 'neighbor_list'
CHASSIS_ID = 'chassis_id'

#get actual system/chassis id
system_id = ''
chassis_id = ''

#File locations details
YAML_RESP_FILE = 'volatile:ignite_resp.yml'
TASK_FILE_LOC = 'volatile:'

#YAML package download and import
YAML_DOWNLOAD_LOC = 'bootflash:poap/'
yaml_download_loc_u = '/bootflash/poap/'
YAML_DOWNLOAD_LOC_TEMP = 'volatile:'
yaml_lib_src = ''

#Log levels and Facility
FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

LEVEL = {
    'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}

#syslog server and port
SYSLOG_SERVER = ignite_hostname
SYSLOG_PORT = 514

#POAP log info
LOG_FILE_HANDLE = ''


def load_yaml():
    try:
        import yaml
    except:
        poap_log("YAML module not found")
        status = False
        status = yaml_pkg_exist()
        if not status:
            get_yaml_module()


def ignored_ext(file_name):
    ext = file_name.split('.')[-1]
    if ext == 'tar':
        return True
    return False


def yaml_pkg_exist():
    yaml_lib_path = ''
    pkg_name_exp = 'PyYAML'
    dir_list = os.listdir(yaml_download_loc_u)
    for dir in dir_list:
        if pkg_name_exp in dir:
            if not ignored_ext(dir):
                yaml_lib_path = "%s/%s/lib" % (yaml_download_loc_u, dir)
                poap_log("YAML pkg found(1) at %s/%s" % (yaml_download_loc_u, dir))
            else:
                pkg_name = os.path.splitext(dir)[0]
                if pkg_name in dir_list:
                    yaml_lib_path = "%s/%s/lib" % (yaml_download_loc_u,
                                                   pkg_name)
                    poap_log("YAML pkg found(2) at %s/%s" % (yaml_download_loc_u, dir))
                else:
                    yaml_tar_path = '%s/%s' % (YAML_DOWNLOAD_LOC, dir)
                    untar(yaml_tar_path, YAML_DOWNLOAD_LOC)
                    yaml_lib_path = "%s/%s/lib" % (yaml_download_loc_u,
                                                   pkg_name)

            if yaml_lib_path:
                import_yaml_module(yaml_lib_path)
                return True

    return False


def import_yaml_module(yaml_lib_path):
    poap_log("YAMP path to import: %s" % yaml_lib_path)
    try:
        sys.path.append(yaml_lib_path)
    except:
        abort_cleanup_exit()


def get_yaml_module():
    global yaml_lib_src
    poap_log("Downloading YAML lib from %s" % yaml_lib_src)
    access_protocol = 'scp'
    hostname = ignite_hostname
    port = ''
    username = ignite_username
    password = ignite_password
    file_src = yaml_lib_src
    file_dst_temp = YAML_DOWNLOAD_LOC_TEMP
    copy_status = get_file(access_protocol, hostname, port,
                           username, password, file_src, file_dst_temp)

    if copy_status:
        pkg_name = os.path.basename(yaml_lib_src)
        file_src = "%s%s" % (file_dst_temp, pkg_name)
        untar(file_src, YAML_DOWNLOAD_LOC)
        pkg_name = os.path.splitext(pkg_name)[0]
        yaml_lib_path = yaml_download_loc_u + pkg_name + '/lib'
        import_yaml_module(yaml_lib_path)
    else:
        abort_cleanup_exit()


def syslog(message, level=LEVEL['notice'], facility=FACILITY['daemon'],
           host='localhost', port=514):
    """
    Send syslog UDP packet to given host and port.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = '<%d>%s' % (level + facility*8, message)
    sock.sendto(data, (host, port))
    sock.close()


def setup_log_file():
    log_filename = '/bootflash/poap.log'
    #now=cli("show clock | sed 's/[ :]/_/g'")
    now = 1
    try:
        log_filename = "%s.%s" % (log_filename, now)
    except Exception as inst:
        print inst
    global LOG_FILE_HANDLE
    LOG_FILE_HANDLE = open(log_filename, "w+")


def poap_log(info):
    global LOG_FILE_HANDLE
    LOG_FILE_HANDLE.write(info)
    LOG_FILE_HANDLE.write("\n")
    LOG_FILE_HANDLE.flush()
    info = system_id + " : poap.py : " + info
    syslog(info, level=5, facility=3, host=SYSLOG_SERVER, port=SYSLOG_PORT)
    sys.stdout.flush()


def poap_log_close():
    LOG_FILE_HANDLE.close()

#Log set ends


def untar(file_src, file_dst):
    cmd = "tar extract %s to %s" % (file_src, file_dst)
    run_cli(cmd)


def run_cli(cmd):
    poap_log("CLI : %s" % cmd)
    return cli(cmd)


def rm_rf(filename):
    try:
        cli("delete %s" % filename)
    except:
        pass


# signal handling
def sig_handler_no_exit(signum, frame):
    poap_log("INFO: SIGTERM Handler while configuring boot variables")
    pass


def sigterm_handler(signum, frame):
    poap_log("INFO: SIGTERM Handler")
    abort_cleanup_exit()
    exit(1)


def abort_cleanup_exit():
    poap_log("INFO: cleaning up")
    send_switch_status(False)
    poap_log_close()
    exit(1)


def wait_box_online():
    while 1:
        r = int(run_cli("show system internal platform internal info | grep box_online | sed 's/[^0-9]*//g'").strip('\n'))
        if r == 1:
            break
        else:
            time.sleep(5)
        poap_log("INFO: Waiting for box online...")


def get_file(access_protocol='', hostname='', port='', username='', password='', file_src='', file_dst='', vrf='management'):
    poap_log("Start copy of task %s" % file_src)
    rm_rf(file_dst)

    if access_protocol == PROTO_SCP:
        cmd = "terminal dont-ask ; terminal password %s ; " % password
        cmd += "copy %s://%s@%s%s %s vrf %s" % (access_protocol, username, hostname, file_src, file_dst, vrf)

    if access_protocol == PROTO_TFTP:
        file_src = os.path.basename(file_src)

        if port:
            cmd = "copy %s://%s:%s/%s %s vrf %s" % (access_protocol, hostname, port, file_src, file_dst, vrf)
        else:
            cmd = "copy %s://%s/%s %s vrf %s" % (access_protocol, hostname, file_src, file_dst, vrf)

    if access_protocol == PROTO_SFTP:
        cmd = "terminal dont-ask ; terminal password %s ; " % password
        cmd += "copy %s://%s@%s%s %s vrf %s" % (access_protocol, username, hostname, file_src, file_dst, vrf)

    if access_protocol == PROTO_HTTP:
        cmd = "copy %s://%s%s %s vrf %s" % (access_protocol, hostname, file_src, file_dst, vrf)

    try:
        run_cli(cmd)
        return True
    except:
        poap_log("Failed to Copy file")
        return False


def get_yaml_file(ignite_resp_data):
    global yaml_lib_src
    yaml_lib_src = ignite_resp_data[RESP_YAML_LIB_PATH]
    file_src = ignite_resp_data[RESP_FILE_SRC]
    hostname = ignite_resp_data[RESP_HOSTNAME]
    #port = ignite_resp_data[RESP_PORT]
    access_protocol = ignite_resp_data[RESP_ACCESS_METHOD]
    username = ignite_resp_data[RESP_USERNAME]
    password = ignite_resp_data[RESP_PASSWORD]
    return get_file(access_protocol, hostname, port, username, password, file_src, YAML_RESP_FILE)


def send_cdp_neigh_info(ignite_req):
    ignite_req = urllib2.Request(IGNITE_URL_CDP, ignite_req, REQUEST_PARAMS)
    ignite_response = urllib2.urlopen(ignite_req)
    ignite_resp_json = ignite_response.read()
    resp_data = json.loads(ignite_resp_json)

    if not resp_data[RESP_STATUS]:
        poap_log("Ignite server response status is Flase with error message: %s"
                 % resp_data[RESP_ERR])
        abort_cleanup_exit()

    poap_log("Ignite response")
    poap_log("file_src: %s hostname: %s: access_protocol: %s username: %s password: %s"
             % (resp_data[RESP_FILE_SRC], resp_data[RESP_HOSTNAME],
             resp_data[RESP_ACCESS_METHOD], resp_data[RESP_USERNAME],
             resp_data[RESP_PASSWORD]))

    return resp_data


def send_switch_status(status):
    data = dict()
    data[SERIAL_NUM] = system_id
    data[RESP_STATUS] = status
    poap_log("Status update request on %s: %s-%s"
             % (IGNITE_URL_STATUS, system_id, status))
    req = urllib2.Request(IGNITE_URL_STATUS, json.dumps(data), REQUEST_PARAMS)
    urllib2.urlopen(req)


def do_no_shut_intf():
    interface_list = json.loads(clid("show interface status"))
    no_shut_intf = "conf t"
    for interface in interface_list['TABLE_interface']['ROW_interface']:
        no_shut_intf = no_shut_intf + " ; interface " + interface['interface'] + " ; no shut"
    cli(no_shut_intf)


def get_cdp_neigh_info():
    do_no_shut_intf()
    #Wait for CDP timeout time before collecting cdp neigh info
    time.sleep(int(cli("show cdp global | grep Refresh | awk '{print $4}'").strip('\n')) + 1)
    cdp_nei = clid("show cdp neigh")
    json_cdp_nei = json.loads(cdp_nei)
    cdp_row_det = json_cdp_nei['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
    neighbours = []

    if(type(cdp_row_det) == dict):
        cdp_det = [{}]
        cdp_det[0] = cdp_row_det
        cdp_row_det = cdp_det

    for row in cdp_row_det:
        cdp_nei_det = {}
        cdp_nei_det['local_port'] = str(row['intf_id'])
        cdp_nei_det['remote_port'] = str(row['port_id'])
        cdp_nei_det['remote_node'] = str(row['device_id']).split('(')[0]
        neighbours.append(cdp_nei_det)
        poap_log("Indiv Neighbour append done")

    req_data = {}
    req_data[SERIAL_NUM] = system_id
    req_data[CHASSIS_ID] = chassis_id
    req_data[NEIGHBOR_LIST] = neighbours
    return(json.dumps(req_data))


def set_system_info():
    global system_id
    global chassis_id
    system_info = json.loads(clid("show version"))
    system_id = str(system_info['proc_board_id'])
    chassis_id = str(system_info['chassis_id'])


def fetch_task():
    import yaml
    yaml_file_u = YAML_RESP_FILE.replace(':', '/')
    yaml_file_u = "/" + yaml_file_u
    yaml_file_fh = open(yaml_file_u, 'r')

    task_data = yaml.load(yaml_file_fh)
    task_list = task_data[TASK_LIST]
    loc_list = task_data[LOCATION_LIST]
    poap_log(str(task_list))
    poap_log(str(loc_list))

    loc_name_list = []
    for loc_name in loc_list.iterkeys():
        loc_name_list.append(loc_name)

    poap_log(str(loc_name_list))

    for task in task_list:
        loc_name = task[TASK_LOC]
        if loc_name:
            if loc_name not in loc_name_list:
                poap_log("Location-%s not found for task-%s"
                         % (loc_name, "task"))
                abort_cleanup_exit()

    copy_status = False

    #start fetching the tasks
    for task in task_list:
        copy_status = True
        loc = loc_list[task[TASK_LOC]]
        poap_log("\n\n %s" % (str(loc)))
        access_protocol = loc[ACCESS_PROTOCOL]
        username = loc[USERNAME]
        password = loc[PASSWORD]
        hostname = loc[HOSTNAME]
        file_src = task[TASK_HANDLER]
        file_dst = TASK_FILE_LOC + os.path.basename(file_src)
        copy_status = get_file(access_protocol, hostname, port,
                               username, password, file_src, file_dst)
        poap_log("Task fetch sucess")

        if not copy_status:
            poap_log("Fetch failed for task %s" % file_src)
            abort_cleanup_exit()
        poap_log("Copy complete")
        task.update({TASK_DST: file_dst})

    return task_list


def import_module(task):
    task_dst = (task[TASK_DST])
    task_dst = '/' + task_dst.replace(':', '/')
    import_name = ((((task_dst.split("/"))[-1]).split('.'))[0])
    poap_log("task_dst = %s" % task_dst)
    poap_log("import_name = %s" % import_name)
    module = ""

    try:
        module = imp.load_source(import_name, task_dst)
        task.update({MODULE_NAME: module})
        poap_log("Loaded  module: %s" % (str(module)))
    except:
        poap_log("Failed to load the module: %s" % import_name)
        abort_cleanup_exit()


def create_process(task):
    module = task[MODULE_NAME]
    target_name = eval("%s.%s" % ("module", task[TASK_FUNCTION]))
    param_dict = task[TASK_PARAMETER]
    proc_name = task[TASK_NAME]

    if not param_dict:
        proc_args = dict({"target": target_name, 'name': proc_name})
    else:
        proc_args = dict({"target": target_name, 'name': proc_name,
                         "kwargs": param_dict})

    proc = multiprocessing.Process(**proc_args)
    task.update({PROC_HANDLE: proc})


def run_process(task):
    proc = task[PROC_HANDLE]
    proc.start()
    proc.join()


def exec_task(task_list):

    for task in task_list:
        import_module(task)

    for task in task_list:
        create_process(task)

    for task in task_list:
        run_process(task)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sig_handler_no_exit)
    setup_log_file()
    set_system_info()
    poap_log("Started execution of poap script")
    req_data = get_cdp_neigh_info()
    ignite_response = send_cdp_neigh_info(req_data)
    get_yaml_file(ignite_response)
    load_yaml()
    task_list = fetch_task()
    exec_task(task_list)
    send_switch_status(True)
    poap_log("Completed execution of poap script")
    exit(0)
