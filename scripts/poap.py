#!/bin/env python
#md5sum=<7521e0b0b04278c488d57dd022e8433b>

from cli import *
import imp
import json
import multiprocessing
import os
import signal
import socket
import sys
import tarfile
import time
import urllib2


#Ignite server access details - fill in from ignite/config.py
ignite_username = "admin"
ignite_password = "cisco123"
ignite_hostname = "172.31.219.250"
ignite_port = "80"
vrf = "management"

#non editable
IGNITE_REST_API_CDP = '/api/bootstrap'
IGNITE_URL_CDP = "http://%s:%s%s" % (ignite_hostname, ignite_port, IGNITE_REST_API_CDP)
IGNITE_REST_API_STATUS = '/api/bootstrap/status'
IGNITE_URL_STATUS = "http://%s:%s%s" % (ignite_hostname, ignite_port, IGNITE_REST_API_STATUS)
REQUEST_PARAMS = {'Content-Type': 'application/json'}

#switch response parameter
MODEL_TYPE = "model_type"

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
RETRY_COUNT = 5

#File locations details

VOLATILE = 'volatile:'
VOLATILE_U = '/volatile'
BOOTFLASH_U = "/bootflash"
POAP_DIR = 'bootflash:poap'
POAP_DIR_U = '/bootflash/poap'
yaml_lib_src = ''
yaml_response_file = ''

#Replay file tag
REPLAY_FILE_TAG = 'poap_replay'

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


def load_yaml(access_protocol):
    try:
        import yaml
    except:
        poap_log("YAML module not found")
        status = False
        status = yaml_pkg_exist()
        if not status:
            get_yaml_module(access_protocol)


def yaml_pkg_exist():
    global yaml_lib_src
    yaml_lib_path = ''
    pkg_name = os.path.basename(yaml_lib_src)
    yaml_lib_path = os.path.join(POAP_DIR_U, pkg_name, 'lib')
    if os.path.isdir(yaml_lib_path):
        poap_log("YAML pkg found(1)- at %s" %yaml_lib_path)
        import_yaml_module(yaml_lib_path)
        return True
    return False


def import_yaml_module(yaml_lib_path):
    poap_log("YAMP path to import: %s" % yaml_lib_path)
    try:
        sys.path.append(yaml_lib_path)
    except:
        cleanup_exit(1)


def get_yaml_module(access_protocol):
    global yaml_lib_src
    poap_log("Downloading YAML lib from %s" % yaml_lib_src)
    hostname = ignite_hostname
    port = ''
    username = ignite_username
    password = ignite_password
    file_src = yaml_lib_src
    pkg_name = os.path.basename(file_src)
    file_dst_temp = "%s%s" %(VOLATILE, pkg_name)
    copy_status = get_file(access_protocol, hostname, port,
                           username, password, file_src, file_dst_temp)

    if copy_status:
        file_dst_temp_u = os.path.join(VOLATILE_U, pkg_name)
        untar(file_dst_temp_u, POAP_DIR_U)
        pkg_name = os.path.splitext(pkg_name)[0].split('.')
        pkg_name = '.'.join(pkg_name[0:-1])
        yaml_lib_path = os.path.join(POAP_DIR_U, pkg_name, 'lib')
        import_yaml_module(yaml_lib_path)
    else:
        cleanup_exit(1)


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
    t=time.localtime()
    now="%d_%d_%d" % (t.tm_hour, t.tm_min, t.tm_sec)
    #now = 1
    try:
        log_filename = "%s.%s" % (log_filename, now)
    except Exception as inst:
        pass
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
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.close()

#Log set ends


def create_poap_dir():
    if os.path.isdir(POAP_DIR_U):
        poap_log("Exists- %s" %POAP_DIR_U)
    else:
        poap_log("Create %s" %POAP_DIR_U)
        try:
            os.mkdir(POAP_DIR_U)
            poap_log("Created")
        except OSError:
            poap_log("Could not create")
            cleanup_exit(1)


def untar(file_src, file_dst):
    poap_log("untar - src %s:, dst : %s" %(file_src, file_dst))
    tf = tarfile.open(file_src, 'r')
    tf.extractall(file_dst)
    #cmd = "tar extract %s to %s" % (file_src, file_dst)
    #run_cli(cmd)


def run_cli(cmd):
    poap_log("CLI : %s" % cmd)
    return cli(cmd)


def rm_rf(filename):
    filename_u = "/" + filename.replace(":", "/")
    if not os.path.exists(filename_u):
        poap_log("rm_rf : Does not exists- %s" %filename_u)
        return
    try:
        run_cli("delete %s" %filename)
        poap_log("Delted")
    except:
        poap_log("Could not delete")
        cleanup_exit(1)


# signal handling
def sig_handler_no_exit(signum, frame):
    poap_log("INFO: SIGTERM Handler while configuring boot variables")
    pass


def sigterm_handler(signum, frame):
    poap_log("INFO: SIGTERM Handler")
    exit(1)


def del_replay_cfg():
   replay_files = os.listdir(BOOTFLASH_U)
   poap_log("Removing previous replay files")
   for filename in replay_files:
       if REPLAY_FILE_TAG in filename:
           poap_log("Replay file found -%s" %filename)
           try:
               os.remove(os.path.join(BOOTFLASH_U, filename))
               poap_log("Deleted")
           except OSError:
               poap_log("Could not delete")


def cleanup_exit(exit_code):
    poap_log("INFO: cleaning up - exit code %s" %exit_code)
    if exit_code:
        del_replay_cfg()
        send_switch_status(False)
    poap_log_close()
    exit(exit_code)


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
        cmd = "terminal password %s ; " % password
        cmd += "copy %s://%s@%s%s %s vrf %s" % (access_protocol, username, hostname, file_src, file_dst, vrf)

    if access_protocol == PROTO_TFTP:

        if port:
            cmd = "copy %s://%s:%s/%s %s vrf %s" % (access_protocol, hostname, port, file_src, file_dst, vrf)
        else:
            cmd = "copy %s://%s/%s %s vrf %s" % (access_protocol, hostname, file_src, file_dst, vrf)

    if access_protocol == PROTO_SFTP:
        cmd = "terminal password %s ; " % password
        cmd += "copy %s://%s@%s%s %s vrf %s" % (access_protocol, username, hostname, file_src, file_dst, vrf)

    if access_protocol == PROTO_HTTP:
        cmd = "copy %s://%s%s %s vrf %s" % (access_protocol, hostname, file_src, file_dst, vrf)

    try:
        cmd = "terminal dont-ask ; " + cmd
        run_cli(cmd)
        return True
    except:
        poap_log("Failed to Copy file")
        return False


def get_yaml_file(ignite_resp_data):
    global yaml_lib_src
    global yaml_response_file
    yaml_lib_src = ignite_resp_data[RESP_YAML_LIB_PATH]
    file_src = ignite_resp_data[RESP_FILE_SRC]
    hostname = ignite_resp_data[RESP_HOSTNAME]
    #port = ignite_resp_data[RESP_PORT]
    access_protocol = ignite_resp_data[RESP_ACCESS_METHOD]
    username = ignite_resp_data[RESP_USERNAME]
    password = ignite_resp_data[RESP_PASSWORD]
    yaml_response_file = "%s%s" %(VOLATILE, os.path.basename(file_src))
    return get_file(access_protocol, hostname, port, username, password, file_src, yaml_response_file)


def send_cdp_neigh_info(ignite_req):
    ignite_req = urllib2.Request(IGNITE_URL_CDP, ignite_req, REQUEST_PARAMS)
    ignite_response = urllib2.urlopen(ignite_req)
    ignite_resp_json = ignite_response.read()
    resp_data = json.loads(ignite_resp_json)

    if not resp_data[RESP_STATUS]:
        poap_log("Ignite server response status is Flase with error message: %s"
                 % resp_data[RESP_ERR])
        cleanup_exit(1)

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
    data[MODEL_TYPE] = chassis_id
    poap_log("Status update request on %s: %s %s- %s "
             % (IGNITE_URL_STATUS, system_id, status, chassis_id))
    req = urllib2.Request(IGNITE_URL_STATUS, json.dumps(data), REQUEST_PARAMS)
    urllib2.urlopen(req)


def do_no_shut_intf():
    interface_list = json.loads(clid("show interface status"))
    no_shut_intf = "conf t"
    for interface in interface_list['TABLE_interface']['ROW_interface']:
        no_shut_intf = no_shut_intf + " ; interface " + interface['interface'] + " ; no shut"
    run_cli(no_shut_intf)


def get_cdp_neigh_info():
    do_no_shut_intf()
    #Wait for CDP timeout time before collecting cdp neigh info
    #time.sleep(int(run_cli("show cdp global | grep Refresh | awk '{print $4}'").strip('\n')) + 1)
    cmd = "show cdp neigh"
    poap_log("cmd : %s" %cmd)
    cdp_nei = clid(cmd)
    poap_log(cdp_nei)
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
    req_data[MODEL_TYPE] = chassis_id
    req_data[NEIGHBOR_LIST] = neighbours
    json_req_data = json.dumps(req_data)
    poap_log(json_req_data)
    return(json_req_data)


def set_system_info():
    global system_id
    global chassis_id
    counter = 1
    steps = 5
    cmd = "show inv"
    LOG_FILE_HANDLE.write("CLI : %s\n" %cmd)
    LOG_FILE_HANDLE.flush()
    while ((counter <= RETRY_COUNT) and (not system_id or not chassis_id)):
        if counter != 1:
            wait_time = counter * steps;
            info = "Failing to get system info - sleep for %s\n" % wait_time
            LOG_FILE_HANDLE.write(info)
            LOG_FILE_HANDLE.flush()
            time.sleep(wait_time)        
	system_info = json.loads(clid("show inv"))
	system_id = str(system_info['TABLE_inv']['ROW_inv'][0]['serialnum'])
	chassis_id =  str(system_info['TABLE_inv']['ROW_inv'][0]['desc']) 
	info = "Serial number : %s, Chassis : %s\n" %(system_id, chassis_id)
	LOG_FILE_HANDLE.write(info)
	LOG_FILE_HANDLE.flush()

    if not system_id or not chassis_id:
        LOG_FILE_HANDLE.write("Aborting- set_system_info failed")
        LOG_FILE_HANDLE.flush()
        poap_log_close()
        exit(1) 


def fetch_task():
    import yaml
    yaml_file_u = yaml_response_file.replace(':', '/')
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
                cleanup_exit(1)

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
        file_dst = VOLATILE + os.path.basename(file_src)
        copy_status = get_file(access_protocol, hostname, port,
                               username, password, file_src, file_dst)

        if not copy_status:
            poap_log("Fetch failed for task %s" % file_src)
            cleanup_exit(1)
        poap_log("Task fetch success")
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
        cleanup_exit(1)


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
    if proc.exitcode:
        cleanup_exit(1)


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
    LOG_FILE_HANDLE.write("Started execution of poap script-1\n")
    LOG_FILE_HANDLE.flush()
    set_system_info()
    poap_log("system info fetch complete")
    create_poap_dir()
    req_data = get_cdp_neigh_info()
    ignite_response = send_cdp_neigh_info(req_data)
    get_yaml_file(ignite_response)
    load_yaml(ignite_response[RESP_ACCESS_METHOD])
    task_list = fetch_task()
    exec_task(task_list)
    send_switch_status(True)
    poap_log("Completed execution of poap script")
    cleanup_exit(0)
