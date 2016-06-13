import re

from config.constants import PARAM_IDENTIFIER_CONFIGLET, PARAM_EXP_CONFIGLET
from exception import IgniteException

import logging
logger = logging.getLogger(__name__)


ERR_PORTS = "Invalid port numbers"


def parse_file(file_content,
               param_exp=PARAM_EXP_CONFIGLET,
               identifier=PARAM_IDENTIFIER_CONFIGLET):
    param_list = []
    get_parameter_list = re.findall(param_exp, file_content)
    for one_param in get_parameter_list:
        one_param = one_param.strip(identifier)
        if one_param not in param_list:
            param_list.append(one_param)
    return param_list


# converts port number list to single string
# ["1/1", "1/2", "1/3"] -> "1/1-3"
# ["1/1", "1/2", "2/3", "2/5", "2/6"] -> "1/1-3,2/3,2/5-6"
def ports_to_string(ports):
    string = ""

    if not ports:
        logger.warning("Port list is empty!")
        return string

    if ports[0].startswith('mgmt0'):
        logger.debug("port %s is mgmt", ports)
        return ports[0]

    module = ports[0].split("/")[0]
    start = ports[0].split("/")[1]
    end = start

    for port in ports[1:]:
        slot = port.split("/")[0]
        index = port.split("/")[1]
        # logger.debug("slot = %s, index = %s", slot, index)

        if slot == module and int(index) == int(end) + 1:
            # current range continues
            end = index
        else:
            if string:
                string += ","

            # end of current range
            string += module + "/" + start
            if int(end) > int(start):
                string += "-" + end

            # start of new range
            module = slot
            start = index
            end = index

    if string:
        string += ","

    # end of current range
    string += module + "/" + start
    if int(end) > int(start):
        string += "-" + end

    return string


# converts single string of port ranges to list of single port numbers
# "1/1-3" -> ["1/1", "1/2", "1/3"]
# "1/1-3,2/3,2/5-6" -> ["1/1", "1/2", "2/3", "2/5", "2/6"]
def string_to_ports(string):
    ports = list()

    try:
        ranges = string.split(",")

        for item in ranges:
            slot = item.split("/")[0]
            values = item.split("/")[1].split("-")
            start = values[0]

            if len(values) > 1:
                end = values[1]
            else:
                end = start

            # logger.debug("slot = %s, start = %s, end = %s", slot, start, end)

            for index in range(int(start), int(end) + 1 if end else int(start) + 1):
                ports.append(slot + "/" + str(index))
    except:
        raise IgniteException(ERR_PORTS)

    return ports
