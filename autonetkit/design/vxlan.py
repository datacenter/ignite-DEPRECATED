import autonetkit.ank as ank_utils
import autonetkit.log as log
from autonetkit.ank_utils import call_log

def build_vxlan(anm):
    g_in = anm['input']
    g_phy = anm['phy']
    g_l3 = anm['layer3']
    g_vxlan = anm.add_overlay("vxlan")

    if g_in.data.vxlan_global_config:
        g_vxlan.data['vxlan_global_config'] = g_in.data['vxlan_global_config']
    else:
        return

    if g_in.data.profiles:
        g_vxlan.data['profiles'] = g_in.data['profiles']
    g_vxlan.add_nodes_from(g_phy, retain=['label', 'update', 'device_type', 'devsubtype',
                                       'asn', 'specified_int_names',
                                       'profile', 'vxlan_vni_configured'])
    g_vxlan.add_edges_from(g_l3.edges())
    '''
    for link in g_vxlan.edges():
        print link.src.vxlan_vni
    g_vxlan.remove_edges_from([link for link in g_vxlan.edges(
    ) if link.src.asn != link.dst.asn])  # remove inter-AS links


    if 'tenant_info' in g_vxlan.data['vxlan_global']:
        for tenant_in_global_list in g_vxlan.data['vxlan_global']['tenant_info']:
            tenant=[]
            for node in g_vxlan:
                if 'vxlan_vni' in node:
                    for tenant_in_node in node.vxlan_vni:

    '''
