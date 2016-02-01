import autonetkit.ank as ank_utils
import autonetkit.log as log
from autonetkit.ank_utils import call_log

def build_mcast(anm):
    g_in = anm['input']
    g_phy = anm['phy']
    g_l3 = anm['layer3']
    g_mcast = anm.add_overlay("mcast")

    g_mcast.add_nodes_from(g_l3, retain=['label', 'update', 'device_type', 'devsubtype',
                                       'asn', 'specified_int_names',
                                       'profile', 'vxlan_vni_configured'])
    g_mcast.add_edges_from(g_l3.edges())
    ank_utils.copy_attr_from(g_in, g_mcast, "multicast")

    nodes_to_be_removed =[]
    for node in g_mcast:
        if node.multicast is None or node.multicast is False:
            nodes_to_be_removed.append(node)

    g_mcast.remove_nodes_from(nodes_to_be_removed)
    for node in g_mcast:
        for interface in node.interfaces():
            if interface.is_bound:
                interface.pim = 1
