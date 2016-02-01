import autonetkit.ank as ank_utils
import autonetkit.log as log
from autonetkit.ank_utils import call_log
import re

VPC_LINK_TYPE = 'VPC-[1-9][0-9]*Link'
PC_LINK_TYPE = 'PC-[1-9][0-9]*Link'
VPC_MEMBERLINK_TYPE = 'VPC-MemberLink'
PC_GENERIC = 'V?PC-(([1-9][0-9]*)|(Member))Link'

def build_pc(anm):
    g_in = anm['input']

    pc_nodes= []
    for node in g_in:
        for interface in node.portchannel_interfaces():
            pc_nodes.append(node)
            break

    if pc_nodes is None:
        return

    g_pc = anm.add_overlay("port_channel")
    g_pc.add_nodes_from(pc_nodes, retain=['vpc_peer'])
    edges_pc = []
    for edges in g_in.edges():
        if re.search(PC_GENERIC, edges.link_type):
            edges_pc.append(edges)

    g_pc.add_edges_from(edges_pc)

