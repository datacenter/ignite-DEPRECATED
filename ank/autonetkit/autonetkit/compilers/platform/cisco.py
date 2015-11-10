import itertools
import os
from datetime import datetime

import autonetkit
import autonetkit.config
import autonetkit.log as log
import autonetkit.plugins.naming as naming
from autonetkit.ank import sn_preflen_to_network
from autonetkit.ank_utils import call_log
from autonetkit.compilers.device.cisco import (IosBaseCompiler,
                                               IosClassicCompiler,
                                               IosXrCompiler, NxOsCompiler,
                                               StarOsCompiler)
from autonetkit.compilers.platform.platform_base import PlatformCompiler
from autonetkit.nidb import ConfigStanza
import netaddr

class CiscoCompiler(PlatformCompiler):

    """Platform compiler for Cisco"""

    @staticmethod
    def numeric_to_interface_label_ios(x):
        """Starts at GigabitEthernet0/1 """
        x = x + 1
        return "GigabitEthernet0/%s" % x

    @staticmethod
    def numeric_to_portchannel_interface_label_ios(x):
        """Starts at GigabitEthernet0/1 """
        return "port-channel %s" % x

    @staticmethod
    def numeric_to_interface_label_ra(x):
        """Starts at Gi0/1
        #TODO: check"""
        x = x + 1
        return "GigabitEthernet%s" % x

    @staticmethod
    def numeric_to_interface_label_nxos(x):
        return "Ethernet2/%s" % (x + 1)

    @staticmethod
    def numeric_to_interface_label_ios_xr(x):
        return "GigabitEthernet0/0/0/%s" % x

    @staticmethod
    def numeric_to_interface_label_star_os(x):
        return "ethernet 1/%s" % (x + 10)

    @staticmethod
    def numeric_to_interface_label_linux(x):
        return "eth%s" % x

    @staticmethod
    def loopback_interface_ids():
        for x in itertools.count(100):  # start at 100 for secondary
            prefix = IosBaseCompiler.lo_interface_prefix
            yield "%s%s" % (prefix, x)

    @staticmethod
    def interface_ids_ios():
        # TODO: make this skip if in list of allocated ie [interface.name for
        # interface in node]
        for x in itertools.count(0):
            yield "GigabitEthernet0/%s" % x

    @staticmethod
    def interface_ids_csr1000v():
        # TODO: make this skip if in list of allocated ie [interface.name for
        # interface in node]
        for x in itertools.count(0):
            yield "GigabitEthernet%s" % x

    @staticmethod
    def interface_ids_nxos():
        for x in itertools.count(0):
            yield "Ethernet2/%s" % x

    @staticmethod
    def interface_ids_ios_xr():
        for x in itertools.count(0):
            yield "GigabitEthernet0/0/0/%s" % x

    @staticmethod
    def numeric_interface_ids():
        """#TODO: later skip interfaces already taken"""
        for x in itertools.count(0):
            yield x

    @staticmethod
    def numeric_portchannel_ids():
        """#TODO: later skip interfaces already taken"""
        for x in itertools.count(1001):
            yield x

    @staticmethod
    def numeric_vpc_ids(start,end):
        """#TODO: later skip interfaces already taken"""
        for x in itertools.count(start):
            yield x

    #@call_log
    def compile(self):
        self.copy_across_ip_addresses()
        self.compile_devices()
        self.assign_management_interfaces()

    def _parameters(self):
        g_phy = self.anm['phy']
        settings = autonetkit.config.settings
        to_memory = settings['Compiler']['Cisco']['to memory']
        use_mgmt_interfaces = g_phy.data.mgmt_interfaces_enabled

        now = datetime.now()
        if settings['Compiler']['Cisco']['timestamp']:
            timestamp = now.strftime("%Y%m%d_%H%M%S_%f")
            dst_folder = os.path.join(
                "rendered", self.host, timestamp, "cisco")
        else:
            dst_folder = os.path.join("rendered", self.host, "cisco")

        # TODO: use a namedtuple
        return to_memory, use_mgmt_interfaces, dst_folder

    #@call_log
    def compile_devices(self):
        import re
        g_phy = self.anm['phy']

        to_memory, use_mgmt_interfaces, dst_folder = self._parameters()

        if use_mgmt_interfaces:
            log.debug("Allocating VIRL management interfaces")
        else:
            log.debug("Not allocating VIRL management interfaces")

        if g_phy.data.mgmt_block is not None:
            mgmt_address_block = netaddr.IPNetwork(g_phy.data.mgmt_block).iter_hosts()

        if g_phy.data.vpcid_block is not None:
            vpc_re = "([0-9]+)(-)([0-9]+)"
            #vpc_id_start = int(re.search(vpc_re, g_phy.data.vpcid_block).group(1))
            #vpc_id_end = int(re.search(vpc_re, g_phy.data.vpcid_block).group(3))
            #vpc_id_range = vpc_id_end-vpc_id_start
        vpc_id_start = 1
        vpc_id_end = 1000
        vpc_id_range = 999
# TODO: need to copy across the interface name from edge to the interface

# TODO: merge common router code, so end up with three loops: routers, ios
# routers, ios_xr routers

    # TODO: Split out each device compiler into own function

    # TODO: look for unused code paths here - especially for interface
    # allocation

        # store autonetkit_cisco version
        log.debug("Generating device configurations")
        from pkg_resources import get_distribution

        # Copy across indices for external connectors (e.g may want to copy
        # configs)
        external_connectors = [n for n in g_phy
                               if n.host == self.host and n.device_type == "external_connector"]
        for phy_node in external_connectors:
            DmNode = self.nidb.node(phy_node)
            DmNode.indices = phy_node.indices

        g_input = self.anm['input']
        node_profiles = g_input.data['profiles']


        managed_switches = [n for n in g_phy.switches()
        if n.host == self.host
        and n.device_subtype == "managed"]
        for phy_node in managed_switches:
            DmNode = self.nidb.node(phy_node)
            DmNode.indices = phy_node.indices

        numeric_vpc_ids = self.numeric_vpc_ids(vpc_id_start,vpc_id_end)
        for phy_node in g_phy.l3devices(host=self.host):
            loopback_ids = self.loopback_interface_ids()
            # allocate loopbacks to routes (same for all ios variants)
            DmNode = self.nidb.node(phy_node)
            DmNode.add_stanza("render")
            DmNode.indices = phy_node.indices


            #NTP configuration
            DmNode.add_stanza("syslog")

            if g_phy.data.mgmt_block is not None:
                DmNode.add_stanza('mgmt')
                DmNode.mgmt.ip = mgmt_address_block.next()
#           for node_data in phy_node._graph.node:
            for node_id in node_profiles:
                #if DmNode._graph.node[node_data]['profile'] == node_id['id']:
                if not phy_node._graph.node[phy_node.id]['profile'] is None:
                    if phy_node._graph.node[phy_node.id]['profile'] == node_id['id']:
                        if node_id.has_key('configs'):
                            if  node_id['configs'].has_key('ntp'):
                                DmNode.add_stanza("ntp")
                                DmNode.ntp.enabled = node_id['configs']['ntp'].get('enabled')
                                DmNode.ntp.server_ip = node_id['configs']['ntp'].get('server_ip')
                            if  node_id['configs'].has_key('snmp'):
                                DmNode.add_stanza('snmp')
                                DmNode.snmp.enabled = node_id['configs']['snmp'].get('enabled')
                                DmNode.snmp.server=[]
                                for server in node_id['configs']['snmp']['servers']:
                                   snmp_server_stanza =  ConfigStanza(ip = server['ip'],
                                                                      version = server['version'],
                                                                      udp_port=server['udp_port'],
                                                                      community=server['community'])
                                   DmNode.snmp.server.append(snmp_server_stanza)
                                DmNode.snmp.users = []
                                for user_prof in node_id['configs']['snmp']['users']:
                                    snmp_user_stanza = ConfigStanza(user=user_prof['user'],
                                                                auth=user_prof['auth'],
                                                                pwd=user_prof['pwd'],
                                                                priv_passphrase=user_prof['priv_passphrase'],
                                                                engine_id=user_prof['engineID'])
                                    DmNode.snmp.users.append(snmp_user_stanza)
                                DmNode.snmp.features=[]
                                for configs in node_id['configs']['snmp']['features']:
                                    snmp_feature_stanza = ConfigStanza(id=configs['id'], enabled=configs['enabled'])
                                    DmNode.snmp.features.append(snmp_feature_stanza)

                        break
            """for node_id in node_profiles:
                if DmNode._graph.node['profile'] == node_id['id']:
                    DmNode.ntp.enabled = node_profiles[0]['configs']['ntp'].get('enabled')
                    DmNode.ntp.server_ip = node_profiles[0]['configs']['ntp'].get('server_ip')
                    """
            #End ntp config

            #syslog config
            for node_id in node_profiles:
                #if DmNode._graph.node[node_data]['profile'] == node_id['id']:
                if not phy_node._graph.node[phy_node.id]['syslog'] is None:
                    if phy_node._graph.node[phy_node.id]['syslog'] == node_id['id']:
                        DmNode.syslog.enabled = node_id['configs']['syslog'].get('enabled')
                        DmNode.syslog.server_ip = node_id['configs']['syslog'].get('severity')
                        break


            #end syslog config
            for interface in DmNode.loopback_interfaces():
                if interface != DmNode.loopback_zero:
                    interface.id = loopback_ids.next()

            # numeric ids
            numeric_int_ids = self.numeric_interface_ids()
            for interface in DmNode.physical_interfaces():
                phy_numeric_id = phy_node.interface(interface).numeric_id
                if phy_numeric_id is None:
                    # TODO: remove numeric ID code
                    interface.numeric_id = numeric_int_ids.next()
                else:
                    interface.numeric_id = int(phy_numeric_id)

                phy_specified_id = phy_node.interface(interface).specified_id
                if phy_specified_id is not None:
                    interface.id = phy_specified_id

            # numeric ids
            numeric_po_ids = self.numeric_portchannel_ids()
            for interface in DmNode.portchannel_interfaces():
                po_interface = phy_node.interface(interface)
                interface.numeric_id =  int(po_interface.id[po_interface.id.rfind('_')+1:])

                po_specified_id = phy_node.interface(interface).specified_id
                if po_specified_id is not None:
                    interface.id = po_specified_id

                for po_mem_int in DmNode.physical_interfaces():
                    po_mem_interface = phy_node.interface(po_mem_int)
                    if po_mem_interface.id in po_interface.members:
                        po_mem_int.channel_group = interface.numeric_id
                        po_interface_int = po_interface._interface
                        if po_interface_int.has_key('subcat_prot'):
                            if po_interface.subcat_prot == "vpc":
                                po_mem_int.member_port_vpc = 1
                                interface.virt_port_channel = 1
                                DmNode.add_stanza('vpc')
                                DmNode.vpc.domain_id = (po_mem_int.channel_group)%vpc_id_range
                                dest = po_interface_int['interfaces'][0]['description']
                                DmNode.vpc.dest = dest[3:]
                            elif po_interface.subcat_prot == "vpc-member":
                                interface.vpc_member_id = (po_mem_int.channel_group)%1000

        #adding destination ip for vpc over here
        for phy_node in g_phy.l3devices(host=self.host):
            DmNode = self.nidb.node(phy_node)
            if DmNode.vpc:
                dest_id = DmNode.vpc.dest
                for phy_node_1 in g_phy.l3devices(host=self.host):
                    if phy_node_1.id == dest_id:
                        DmNode_1 = self.nidb.node(phy_node_1)
                        DmNode.vpc.dest = DmNode_1.mgmt.ip
                        break


            #from autonetkit.compilers.device.ubuntu import UbuntuCompiler
        #from autonetkit_cisco.compilers.device.ubuntu import UbuntuCompiler

        #ubuntu_compiler = UbuntuCompiler(self.nidb, self.anm)
        for phy_node in g_phy.servers(host=self.host):
            DmNode = self.nidb.node(phy_node)
            DmNode.add_stanza("render")
            DmNode.add_stanza("ip")

            #interface.id = self.numeric_to_interface_label_linux(interface.numeric_id)
            # print "numeric", interface.numeric_id, interface.id
            DmNode.ip.use_ipv4 = phy_node.use_ipv4
            DmNode.ip.use_ipv6 = phy_node.use_ipv6

            # TODO: clean up interface handling
            numeric_int_ids = self.numeric_interface_ids()
            for interface in DmNode.physical_interfaces():
                phy_numeric_id = phy_node.interface(interface).numeric_id
                if phy_numeric_id is None:
                    # TODO: remove numeric ID code
                    interface.numeric_id = numeric_int_ids.next()
                else:
                    interface.numeric_id = int(phy_numeric_id)

                phy_specified_id = phy_node.interface(interface).specified_id
                if phy_specified_id is not None:
                    interface.id = phy_specified_id

            # numeric ids
            numeric_po_ids = self.numeric_portchannel_ids()
            for interface in DmNode.portchannel_interfaces():
                phy_numeric_id = phy_node.interface(interface).numeric_id
                if phy_numeric_id is None:
                    # TODO: remove numeric ID code
                    interface.numeric_id = numeric_po_ids.next()
                else:
                    interface.numeric_id = int(phy_numeric_id)

                phy_specified_id = phy_node.interface(interface).specified_id
                if phy_specified_id is not None:
                    interface.id = phy_specified_id

                # TODO: make this part of the base device compiler, which
                # server/router inherits

            # not these are physical interfaces; configure after previous
            # config steps
            if use_mgmt_interfaces:
                mgmt_int = DmNode.add_interface(
                    management=True, description="eth0")
                mgmt_int_id = "eth0"
                mgmt_int.id = mgmt_int_id

                # render route config
            DmNode = self.nidb.node(phy_node)
            #ubuntu_compiler.compile(DmNode)

            if not phy_node.dont_configure_static_routing:
                DmNode.render.template = os.path.join(
                    "templates", "linux", "static_route.mako")
                if to_memory:
                    DmNode.render.to_memory = True
                else:
                    DmNode.render.dst_folder = dst_folder
                    DmNode.render.dst_file = "%s.conf" % naming.network_hostname(
                        phy_node)

        # TODO: refactor out common logic

        ios_compiler = IosClassicCompiler(self.nidb, self.anm)
        host_routers = g_phy.routers(host=self.host)
        ios_nodes = (n for n in host_routers if n.syntax in ("ios", "ios_xe"))
        for phy_node in ios_nodes:
            if phy_node.devsubtype == "core":
                continue
            DmNode = self.nidb.node(phy_node)
            DmNode.add_stanza("render")
            DmNode.render.template = os.path.join("templates", "ios.mako")
            to_memory = False
            if to_memory:
                DmNode.render.to_memory = True
            else:
                DmNode.render.dst_folder = dst_folder
                DmNode.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            # TODO: write function that assigns interface number excluding
            # those already taken

            # Assign interfaces
            if phy_node.device_subtype == "IOSv":
                int_ids = self.interface_ids_ios()
                numeric_to_interface_label = self.numeric_to_interface_label_ios
            elif phy_node.device_subtype == "CSR1000v":
                int_ids = self.interface_ids_csr1000v()
                numeric_to_interface_label = self.numeric_to_interface_label_ra
            else:
                # default if no subtype specified
                # TODO: need to set default in the load module
                log.warning("Unexpected subtype %s for %s" %
                            (phy_node.device_subtype, phy_node))
                int_ids = self.interface_ids_ios()
                numeric_to_interface_label = self.numeric_to_interface_label_ios
                numeric_to_portchannel_interface_label = self.numeric_to_portchannel_interface_label_ios

            if use_mgmt_interfaces:
                if phy_node.device_subtype == "IOSv":
                    # TODO: make these configured in the internal config file
                    # for platform/device_subtype keying
                    mgmt_int_id = "GigabitEthernet0/0"
                if phy_node.device_subtype == "CSR1000v":
                    mgmt_int_id = "GigabitEthernet1"

            for interface in DmNode.physical_interfaces():
                # TODO: use this code block once for all routers
                if not interface.id:
                    interface.id = numeric_to_interface_label(
                        interface.numeric_id)
                else:
                    if interface.id[0] == 'e' or interface.id[0] == 'E':
                        #import re
                        port_re = "([a-zA-Z]+)([0-9]+/[0-9]+)"
                        interface.id = "%s %s"%((re.search(port_re,interface.id)).group(1),
                                                (re.search(port_re,interface.id)).group(2))

            for interface in DmNode.portchannel_interfaces():
                # TODO: use this code block once for all routers
                #if not interface.id:
                interface.id = numeric_to_portchannel_interface_label(
                        interface.numeric_id)

            ios_compiler.compile(DmNode)
            if use_mgmt_interfaces:
                mgmt_int = DmNode.add_interface(management=True)
                mgmt_int.id = mgmt_int_id

        nxos_compiler = NxOsCompiler(self.nidb, self.anm)
        for phy_node in g_phy.routers(host=self.host, syntax='nx_os'):
            DmNode = self.nidb.node(phy_node)
            DmNode.add_stanza("render")
            DmNode.render.template = os.path.join("templates", "nx_os.mako")
            if to_memory:
                DmNode.render.to_memory = True
            else:
                DmNode.render.dst_folder = dst_folder
                DmNode.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            # Assign interfaces
            int_ids = self.interface_ids_nxos()
            for interface in DmNode.physical_interfaces():
                if not interface.id:
                    interface.id = self.numeric_to_interface_label_nxos(
                        interface.numeric_id)

            DmNode.supported_features = ConfigStanza(
                mpls_te=False, mpls_oam=False, vrf=False)

            nxos_compiler.compile(DmNode)
            # TODO: make this work other way around

            if use_mgmt_interfaces:
                mgmt_int_id = "mgmt0"
                mgmt_int = DmNode.add_interface(management=True)
                mgmt_int.id = mgmt_int_id

        staros_compiler = StarOsCompiler(self.nidb, self.anm)
        for phy_node in g_phy.routers(host=self.host, syntax='StarOS'):
            DmNode = self.nidb.node(phy_node)
            DmNode.add_stanza("render")
            DmNode.render.template = os.path.join("templates", "staros.mako")
            if to_memory:
                DmNode.render.to_memory = True
            else:
                DmNode.render.dst_folder = dst_folder
                DmNode.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            # Assign interfaces
            int_ids = self.interface_ids_nxos()
            for interface in DmNode.physical_interfaces():
                if not interface.id:
                    interface.id = self.numeric_to_interface_label_star_os(
                        interface.numeric_id)

            staros_compiler.compile(DmNode)
            # TODO: make this work other way around

            if use_mgmt_interfaces:
                mgmt_int_id = "ethernet 1/1"
                mgmt_int = DmNode.add_interface(management=True)
                mgmt_int.id = mgmt_int_id

    def assign_management_interfaces(self):
        g_phy = self.anm['phy']
        use_mgmt_interfaces = g_phy.data.mgmt_interfaces_enabled
        if not use_mgmt_interfaces:
            return
        lab_topology = self.nidb.topology(self.host)
        oob_management_ips = {}

        hosts_to_allocate = sorted(self.nidb.l3devices(host=self.host))
        dhcp_subtypes = {"vios"}
        dhcp_hosts = [
            h for h in hosts_to_allocate if h.device_subtype in dhcp_subtypes]

        for DmNode in hosts_to_allocate:
            for interface in DmNode.physical_interfaces():
                if interface.management:
                    interface.description = "OOB Management"
                    interface.physical = True
                    interface.mgmt = True
                    interface.comment = "Configured on launch"
                    if DmNode.ip.use_ipv4:
                        # want a "no ip address" stanza
                        interface.use_ipv4 = False
                    if DmNode.use_cdp:
                        interface.use_cdp = True  # ensure CDP activated
                    if DmNode in dhcp_hosts:
                        interface.use_dhcp = True
