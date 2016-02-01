import autonetkit.ank as ank_utils
import autonetkit.log as log
from autonetkit.ank_utils import call_log

def build_snmp(anm):
    g_in = anm['input']

    if g_in.data.profiles:
        node_profiles = g_in.data['profiles']
    else:
        return

    snmp_nodes =[]
    for node in g_in:
        for prof in node_profiles:
            if node.profile == prof['id']:
                if 'configs' in prof and 'snmp' in prof['configs']:
                    node.snmp = {}
                    if 'enabled' in prof['configs']['snmp'] and prof['configs']['snmp']['enabled'] == 1:##if snmp is enabled then only we add snmp info
                        node.snmp['enabled'] = True
                        if 'servers' in prof['configs']['snmp']:
                            node.snmp['servers'] = []
                            for server in prof['configs']['snmp']['servers']:
                                ## If all parameters are not present we will skip
                                if all(key in server for key in ["ip", "version", "udp_port", "community"]):
                                    server_temp = dict(server)
                                    node.snmp['servers'].append(server_temp)
                        if 'users' in prof['configs']['snmp']:
                            node.snmp['users'] = []
                            for user in prof['configs']['snmp']['users']:
                                ## If all parameters are not present we will skip
                                if all(key in user for key in ["pwd", "engineID", "user", "auth", "priv_passphrase"]):
                                    user_temp = dict(user)
                                    node.snmp['users'].append(user_temp)
                        if 'features' in prof['configs']['snmp']:
                            node.snmp['traps'] = []
                            for trap in prof['configs']['snmp']['features']:
                                ## If all parameters are not present we will skip
                                if all(key in trap for key in ["enabled", "id"]):
                                    trap_temp = dict(trap)
                                    node.snmp['traps'].append(trap_temp)

                        snmp_nodes.append(node)
                break

    if snmp_nodes is None:
        return

    g_snmp = anm.add_overlay("snmp")
    g_snmp.add_nodes_from(snmp_nodes, retain=['snmp'])

    ##no design rules for SNMP as of now


def build_ntp(anm):
    g_in = anm['input']

    if g_in.data.profiles:
        node_profiles = g_in.data['profiles']
    else:
        return

    ntp_nodes =[]
    for node in g_in:
        for prof in node_profiles:
            if node.profile == prof['id']:
                if 'configs' in prof and 'ntp' in prof['configs']:
                    node.ntp = {}
                    feature = prof['configs']['ntp']
                    if all(key in feature for key in ["enabled", "server_ip"]):
                        node.ntp['enabled'] = feature['enabled']
                        node.ntp['server_ip'] = feature['server_ip']
                        ntp_nodes.append(node)
                break

    if ntp_nodes is None:
        return

    g_ntp = anm.add_overlay("ntp")
    g_ntp.add_nodes_from(ntp_nodes, retain=['ntp'])

    ##no design rules for SNMP as of now