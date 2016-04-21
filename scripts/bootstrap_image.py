from cli import *
import json
import os
import socket
import sys
import time


#Set syslog server and port - fill in from ignite/config.py
SYSLOG_SERVER = "172.31.219.250"
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

#Log file handle
LOG_FILE_HANDLE = ""

#Remote log infra
#Log levels and facility
FACILITY = 3
LEVEL = {
    'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}


def close_log_file():
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.close()


def set_log_file():
    log_filename = '/bootflash/poap_image.log'
    t=time.localtime()
    now="%d_%d_%d" % (t.tm_hour, t.tm_min, t.tm_sec)
    #now = 1
    try:
        log_filename = "%s.%s" % (log_filename, now)
    except Exception as inst:
        pass
    global LOG_FILE_HANDLE
    LOG_FILE_HANDLE = open(log_filename, "w+")

def syslog(info, level=LEVEL['info']):
    global LOG_FILE_HANDLE
    LOG_FILE_HANDLE.write(info)
    LOG_FILE_HANDLE.write("\n")
    LOG_FILE_HANDLE.flush()
    message = "%s : %s : %s" % (serial_num_g, os.path.basename(__file__), info)
    data = '<%d>%s' % (level + FACILITY*8, message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (SYSLOG_SERVER, SYSLOG_PORT))
    sock.close()
    sys.stdout.flush()


def cleanup_exit(exit_status):
    syslog("Exiting bootstrap script status: %s" % exit_status)
    close_log_file()
    exit(exit_status)


def rm_rf(filename):
    filename_u = "/" + filename.replace(":", "/")
    if not os.path.exists(filename_u):
        syslog("rm_rm: file does not exist- %s" %filename)
        return True
    try:
        cli("delete %s" % filename)
        syslog("Deleted")
        return True
    except:
        syslog("Could not delete")
        return False


def run_cli(cmd):
    syslog("CLI : %s" % cmd)
    return cli(cmd)


def do_copy(source="", dest=""):

    if not rm_rf(dest):
        return False

    syslog("INFO: Copy started")

    if protocol_g == PROTO_SCP:
        cmd = "terminal dont-ask ; terminal password %s ; " % password_g
        cmd += "copy %s://%s@%s%s %s vrf %s" % (protocol_g, username_g,
                                                hostname_g, source, dest, vrf_g)

    if protocol_g == PROTO_TFTP:

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


def get_image(protocol="scp", port="", hostname="", file_src="",
              file_dst="bootflash:poap/", default_image="",
              vrf="management", username="", password="",
              serial_num="", fatal=True):

    if "" in [protocol, hostname, file_src, file_dst, username, password]:
        cleanup_exit(1)

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

    set_log_file()

    run_cli("terminal dont-ask")

    image_name = os.path.basename(file_src)
    syslog("Image to download %s" % image_name)
    file_dst_local = IMAGE_DST_LOCAL_PATH + image_name
    syslog("Image temp detination %s" % file_dst_local)
    file_dst = file_dst + image_name
    syslog("Image final detination %s" % file_dst)

    if not rm_rf(file_dst_local):
	if not fatal:
            cleanup_exit(0)

        cleanup_exit(1)


    #will set default image (full path)
    if default_image == "":
        default_image = file_dst
        #default_image = default_image_g
        syslog("Default image is %s" % default_image)

    md5_file_name_src = "%s.%s" % (file_src, MD5SUM_EXT)
    md5_file_name_dst = "%s%s_poap_md5.md5" % (IMAGE_DST_LOCAL_PATH,
                                               image_name)
    syslog("INFO: Start fetching md5 source")

    if not do_copy(md5_file_name_src, md5_file_name_dst):

        if not fatal:
            cleanup_exit(0)

        cleanup_exit(1)

    #check if the current/default and intended images are same
    if not same_md5(default_image, md5_file_name_dst):
        default_image_u = '/' + default_image.replace(':', '/')

        if os.path.exists(default_image_u):
            syslog("Exists %s" % default_image)

            if os.path.basename(default_image_u) == image_name:
                syslog("Image files have different md5 but same name")
                syslog("Delete existing image file")
                if not rm_rf(default_image):

		    if fatal:
			cleanup_exit(1)

		    cleanup_exit(0)

        else:
            syslog("Does not exist %s" % default_image)


        if not do_copy(file_src, file_dst_local):

            if fatal:
                cleanup_exit(1)

            cleanup_exit(0)

        syslog("INFO: Completed Copy of System Image")

        #check if the downloaded image md5 matches the md5 calculated at source
        if not same_md5(file_dst_local, md5_file_name_dst):

            if not fatal:
                cleanup_exit(1)

            cleanup_exit(0)

        cmd = "copy %s %s ; " % (file_dst_local, file_dst)
        cmd +=  "config terminal ; boot nxos %s ; exit ; " % (file_dst)
        cmd += "copy running-config startup-config ; "
        run_cli(cmd)

    cleanup_exit(0)
