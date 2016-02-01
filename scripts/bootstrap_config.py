from cli import *
import json
import os
import socket
import sys

#Set syslog server and port - fill in from ignite/config.py
SYSLOG_SERVER = "172.31.219.35"
SYSLOG_PORT = 514

md5sum_ext_src = "md5"

#copy parameters
protocol_g = ""
hostname_g = ""
username_g = ""
password_g = ""
vrf_g = ""

#serial number of switch
serial_num = ""

#Remote log infra
#Log levels and facility
FACILITY = 3
LEVEL = {
    'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}


def syslog(info, level=LEVEL['info']):
    message = "%s : %s : %s" % (serial_num, os.path.basename(__file__), info)
    data = '<%d>%s' % (level + FACILITY*8, message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (SYSLOG_SERVER, SYSLOG_PORT))
    sock.close()


def run_cli(cmd):
    syslog("CLI : %s" % cmd)
    return cli(cmd)


def rm_rf(filename):
    try:
        cli("delete %s" % filename)
    except:
        pass


def abort_cleanup_exit(exit_status):
    syslog("INFO: cleaning up")
    exit(exit_status)


def do_copy(file_src, file_dst):
    rm_rf(file_dst)
    cmd = "terminal dont-ask ; terminal password %s ; " % password_g
    cmd += "copy %s://%s@%s%s %s vrf %s" % (protocol_g, username_g,
                                            hostname_g, file_src,
                                            file_dst, vrf_g)

    try:
        run_cli(cmd)
        return True
    except:
        syslog("WARN: Copy Failed: %s" % str(sys.exc_value).strip('\n\r'))
        return False


def get_md5sum_src(file_name):
    md5_file_name_src = "%s.%s" % (file_name, md5sum_ext_src)
    md5_file_name_dst = "volatile:%s.poap_md5" % os.path.basename(md5_file_name_src)
    syslog("INFO: Start fetching md5 file_src")
    rm_rf(md5_file_name_dst)
    ret = do_copy(md5_file_name_src, md5_file_name_dst)
    sum = 0

    if ret:
        cmd = "show file %s | grep -v '^#' | head lines 1 | sed 's/ .*$//'" % md5_file_name_dst
        sum = run_cli(cmd).strip('\n')
        syslog("INFO: md5sum %s (.md5 file)" % sum)

    return sum


def get_md5sum_dst(file_name):
    cmd = "cat %s  | grep -v '^#' | head -1 | sed 's/ .*$//''" % file_name
    sum = run_cli("show file %s md5sum" % file_name).strip('\n')
    syslog("INFO: md5sum %s (recalculated)" % sum)
    return sum


def check_md5sum(filename_src, filename_dst):
    md5sum_src = get_md5sum_src(filename_src)
    syslog("md5sum_src = %s" % md5sum_src)
    if md5sum_src:  # we found a .md5 file on the server
        md5sum_dst = get_md5sum_dst(filename_dst)
        syslog("md5sum_dst = %s" % md5sum_dst)
        if md5sum_dst != md5sum_src:
            syslog("MD5 verification failed for %s!" % (filename_dst))
            return False
        syslog("MD5 Verification successfull")
    return True


def set_system_info():
    global serial_num
    system_info = json.loads(clid("show version"))
    serial_num = str(system_info['proc_board_id'])


def get_config(protocol="scp", port="", hostname="", file_src="",
               file_dst="volatile:poap.cfg", vrf="management",
               username="", password="", fatal=True):

    if "" in [protocol, hostname, file_src, file_dst, username, password]:

        if fatal:
            abort_cleanup_exit(1)

        abort_cleanup_exit(0)

    global protocol_g
    protocol_g = protocol
    global hostname_g
    hostname_g = hostname
    global username_g
    username_g = username
    global password_g
    password_g = password
    global vrf_g
    vrf_g = vrf

    run_cli("terminal dont-ask")

    set_system_info()

    rm_rf(file_dst)
    status = do_copy(file_src, file_dst)

    if not status:
        syslog("Failed copy of Config file")

        if fatal:
            abort_cleanup_exit(1)

        abort_cleanup_exit(0)

    syslog("Completed copy of Config file")
    status = check_md5sum(file_src, file_dst)

    if not status and fatal:
        syslog("md5sum check failed")
        if fatal:
            abort_cleanup_exit(1)

        abort_cleanup_exit(0)

    run_cli("copy running-config startup-config")
    run_cli('copy %s scheduled-config' % file_dst)
