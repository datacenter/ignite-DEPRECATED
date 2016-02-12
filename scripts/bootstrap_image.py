from cli import *
import json
import os
import socket
import sys


#Set syslog server and port - fill in from ignite/config.py
SYSLOG_SERVER = "127.0.0.1"
SYSLOG_PORT = 514

MD5SUM_EXT = "md5"
IMAGE_DST_LOCAL_PATH = "volatile:"

#copy parameters
protocol_g = ""
port_g = ""
hostname_g = ""
username_g = ""
password_g = ""
vrf_g = ""

#Access protocols
PROTO_SCP = 'scp'
PROTO_TFTP = 'tftp'
PROTO_SFTP = 'sftp'
PROTO_HTTP = 'http'

#serial number of switch
serial_num_g = ""
#default image of switch
default_image_g = ""

#Remote log infra
#Log levels and facility
FACILITY = 3
LEVEL = {
    'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}


def syslog(info, level=LEVEL['info']):
    message = "%s : %s : %s" % (serial_num_g, os.path.basename(__file__), info)
    data = '<%d>%s' % (level + FACILITY*8, message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (SYSLOG_SERVER, SYSLOG_PORT))
    sock.close()


def abort_cleanup_exit(exit_status):
    syslog("Exiting bootstrap script status: %s" % exit_status)
    exit(exit_status)


def rm_rf(filename):
    try:
        cli("delete %s" % filename)
    except:
        pass


def run_cli(cmd):
    syslog("CLI : %s" % cmd)
    return cli(cmd)


def do_copy(source="", dest=""):
    rm_rf(dest)
    syslog("INFO: Copy started")

    if protocol_g == PROTO_SCP:
        cmd = "terminal dont-ask ; terminal password %s ; " % password_g
        cmd += "copy %s://%s@%s%s %s vrf %s" % (protocol_g, username_g,
                                                hostname_g, source, dest, vrf_g)

    if protocol_g == PROTO_TFTP:
        source = os.path.basename(source)

        if port_g:
            cmd = "copy %s://%s:%s/%s %s vrf %s" % (protocol_g, hostname_g,
                                                    port_g, source, dest, vrf_g)
        else:
            cmd = "copy %s://%s/%s %s vrf %s" % (protocol_g, hostname_g,
                                                 source, dest, vrf_g)

    if protocol_g == PROTO_SFTP:
        cmd = "terminal dont-ask ; terminal password %s ; " % password_g
        cmd += "copy %s://%s@%s%s %s vrf %s" % (protocol_g, username_g,
                                                hostname_g, source, dest, vrf_g)

    if protocol_g == PROTO_HTTP:
        cmd = "copy %s://%s%s %s vrf %s" % (protocol_g, hostname_g,
                                            source, dest, vrf_g)

    try:
        run_cli(cmd)
        return True
    except:
        syslog("Copy Failed: %s" % str(sys.exc_value).strip('\n\r'))
        return False


def get_md5sum_bin(bin_file):
    sum = run_cli("show file %s md5sum" % bin_file).strip('\n')
    syslog("INFO: md5sum %s (recalculated)" % sum)
    return sum


def get_md5sum_md5file(md5_file):
    sum = run_cli("show file %s | grep -v '^#' | head lines 1 | sed 's/ .*$//'" % md5_file).strip('\n')
    syslog("INFO: md5sum %s (grep-ed)" % sum)
    return sum


def same_md5(bin_file, md5_file):
    syslog("paths- bin_file: %s - md5_file: %s" % (bin_file, md5_file))
    bin_file_linux = '/' + bin_file.replace(':', '/')

    if os.path.exists(bin_file_linux):
        syslog("INFO : Same image check started")
        md5sum_src = get_md5sum_md5file(md5_file)

        if md5sum_src:
            md5sum_dst = get_md5sum_bin(bin_file)

            if md5sum_dst == md5sum_src:
                syslog("Same source and destination images")
                return True

    syslog("Different source and destination images")
    return False


def set_system_info():
    global default_image_g
    system_info = json.loads(clid("show version"))
    default_image_g = str(system_info['kick_file_name'])


def get_image(protocol="scp", port="", hostname="", file_src="",
              file_dst="bootflash:poap/", default_image="",
              vrf="management", username="", password="",
              serial_num="", fatal=True):

    if "" in [protocol, hostname, file_src, file_dst, username, password]:
        abort_cleanup_exit()

    global protocol_g
    protocol_g = protocol
    global port_g
    port_g = port
    global hostname_g
    hostname_g = hostname
    global username_g
    username_g = username
    global password_g
    password_g = password
    global vrf_g
    vrf_g = vrf
    global serial_num_g
    serial_num_g = serial_num

    run_cli("terminal dont-ask")

    set_system_info()

    image_name = (file_src.split('/'))[-1]
    syslog("Image to download %s" % image_name)
    file_dst_local = IMAGE_DST_LOCAL_PATH + image_name
    syslog("Image temp detination %s" % file_dst_local)
    file_dst = file_dst + image_name
    syslog("Image final detination %s" % file_dst)
    rm_rf(file_dst_local)

    #will set default image (full path)
    if default_image == "":
        default_image = default_image_g
        syslog("Default image is %s" % default_image)

    md5_file_name_src = "%s.%s" % (file_src, MD5SUM_EXT)
    md5_file_name_dst = "%s%s_poap_md5.md5" % (IMAGE_DST_LOCAL_PATH,
                                               image_name)
    rm_rf(md5_file_name_dst)
    syslog("INFO: Start fetching md5 source")

    if not do_copy(md5_file_name_src, md5_file_name_dst):

        if not fatal:
            abort_cleanup_exit(0)

        abort_cleanup_exit(1)

    #check if the current/default and intended images are same
    if not same_md5(default_image, md5_file_name_dst):

        if not do_copy(file_src, file_dst_local):

            if fatal:
                abort_cleanup_exit(1)

            abort_cleanup_exit(0)

        syslog("INFO: Completed Copy of System Image")

        #check if the downloaded image md5 matches the md5 calculated at source
        if not same_md5(file_dst_local, md5_file_name_dst):

            if not fatal:
                abort_cleanup_exit(1)

            abort_cleanup_exit(0)

        cmd = "copy %s %s" % (file_dst_local, file_dst)
        run_cli(cmd)
        cmd = "config terminal ; boot nxos %s" % (file_dst)
        run_cli(cmd)
        cmd = "copy running-config startup-config"
        run_cli(cmd)

    exit(0)
