import requests
import json
import sys
import os

sys.path.append(os.path.join(os.path.join(os.getcwd(), "..")))

from ignite.conf import IGNITE_IP, IGNITE_PORT


linecards = [
{
    "name": "Cisco Nexus M6PQ",
    "lc_type": "Module",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 6,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus M8PQ",
    "lc_type": "Module",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 8,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus M12PQ",
    "lc_type": "Module",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 12,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-M2PC-CFP2",
    "lc_type": "Module",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 2,
                "speed": "100G",
                "transceiver": "CFP2",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-M4PC-CFP2",
    "lc_type": "Module",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 4,
                "speed": "100G",
                "transceiver": "CFP2",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9536PQ",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 32,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Both"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9636PQ",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 36,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Both"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9432PQ",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 32,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Both"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9564PX",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver": "SFP+",
                "role": "Downlink"
            },
			{
                "num_ports": 4,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9564TX",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver": "GBASE-T",
                "role": "Downlink"
            },
			{
                "num_ports": 4,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9464PX",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver": "SFP+",
                "role": "Downlink"
            },
			{
                "num_ports": 4,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9464PX-48",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver": "SFP+",
                "role": "Downlink"
            },
			{
                "num_ports": 4,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9464TX",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver": "GBASE-T",
                "role": "Downlink"
            },
			{
                "num_ports": 4,
                "speed": "40G",
                "transceiver": "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9432C-S",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 32,
                "speed": "100G",
                "transceiver": "QSFP28",
                "role": "Both"
            }
        ]
    }
},

{
    "name": "Cisco Nexus N9K-X9408PC-CFP2",
    "lc_type": "Linecard",
    "lc_data": {
        "port_groups": [
            {
                "num_ports": 8,
                "speed": "100G",
                "transceiver": "CFP2",
                "role": "Both"
            }
        ]
    }
}
]

models =  [
{
    "name": "Cisco Nexus 9332PQ",
    "base_model": "93xx", "switch_type": "Fixed",
    "switch_data": {
        "tiers": ["Core", "Spine", "Leaf", "Border"],
        "port_groups": [
            {
                "num_ports": 32,
                "speed": "40G",
                "transceiver" : "QSFP+",
                "role": "Both"
            }
        ]
    }
},

{
    "name": "Cisco Nexus 9372PX",
    "base_model": "93xx", "switch_type": "Fixed",
    "switch_data": {
        "tiers": ["Leaf", "Border"],
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver" : "SFP+",
                "role": "Downlink"
            },
            {
                "num_ports": 6,
                "speed": "40G",
                "transceiver" : "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus 93120TX",
    "base_model": "93xx", "switch_type": "Fixed",
    "switch_data": {
        "tiers": ["Leaf", "Border"],
        "port_groups": [
            {
                "num_ports": 96,
                "speed": "1/10G",
                "transceiver" : "GBASE-T",
                "role": "Downlink"
            },
            {
                "num_ports": 6,
                "speed": "40G",
                "transceiver" : "QSFP+",
                "role": "Uplink"
            }
        ]
    }
},

{
    "name": "Cisco Nexus 9396PX with M6PQ",
    "base_model": "93xx", "switch_type": "Fixed",
    "switch_data": {
        "tiers": ["Leaf", "Border"],
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver" : "SFP+",
                "role": "Downlink"
            }
        ],
        "module_id": 1
    }
},

{
    "name": "Cisco Nexus 9396PX with M12PQ",
    "base_model": "93xx", "switch_type": "Fixed",
    "switch_data": {
        "tiers": ["Leaf", "Border"],
        "port_groups": [
            {
                "num_ports": 48,
                "speed": "1/10G",
                "transceiver" : "SFP+",
                "role": "Downlink"
            }
        ],
        "module_id": 3
    }
},

{
    "name": "Cisco Nexus 9504 w/ 2 * 9536PQ",
    "base_model": "95xx", "switch_type": "Chassis",
    "switch_data": {
        "tiers": ["Core", "Spine"],
        "num_slots": 4,
        "slots" : [
            { "slot_num": 1, "lc_id": 6 },
            { "slot_num": 2, "lc_id": 6 }
        ]
    }
},

{
    "name": "Cisco Nexus 9504 w/ 2 * 9636PQ",
    "base_model": "95xx", "switch_type": "Chassis",
    "switch_data": {
        "tiers": ["Core", "Spine"],
        "num_slots": 4,
        "slots" : [
            { "slot_num": 2, "lc_id": 7 },
            { "slot_num": 4, "lc_id": 7 }
        ]
    }
}
]


#add linecards, modules and switches
def add_switch():
    auth_key_url = 'http://' + IGNITE_IP + ':' + IGNITE_PORT + '/auth/login/'
    auth_data = {"username": "admin", "password": "admin"}
    auth_header = {"content_type": "application/json"}
    auth_token = requests.post(url=auth_key_url, data=auth_data, headers=auth_header)
    token = json.loads(auth_token.text)["auth_token"]
    header = {"Authorization": token, "content-type": "application/json"}
    for lc in linecards:
        lc_url = 'http://' + IGNITE_IP + ':' + IGNITE_PORT + '/api/switch/linecard'
        requests.post(url=lc_url, data=json.dumps(lc), headers=header)

    for model in models:
        model_url = 'http://' + IGNITE_IP + ':' + IGNITE_PORT + '/api/switch/model'
        requests.post(url=model_url, data=json.dumps(model), headers=header)


add_switch()
