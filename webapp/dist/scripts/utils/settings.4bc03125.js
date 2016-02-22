(function() {
    'use strict';

    /**
     * @ngdoc overview
     * @name clmServiceRequestApp Settings.js
     * @description
     * # clmServiceRequestApp
     "baseURL": "http://127.0.0.1:8000",
     * Store all constant variables here for the clmServiceRequestApp. All data urls will be stored in the constants file.
     */

    angular.module("PoapServer")
        .constant('appSettings', {
            "static" : {
              "baseURL" : "http://localhost:9010"
            },

            //API URL
            "appAPI": {
                "baseURL": "http://127.0.0.1:8000",

                "configlets" : {
                  "list" : {
                     // "url" : "http://localhost:9010/data/configlets-list.json",
                      "url" : "/api/config/configlet",
                      "method" : "GET",
                      "auth" : "true"
                    },
                  "add" : {
                      //"url" : "/data/add-configlets.json",
                      "url" : "/api/config/configlet",
                      //"method" : "GET",
                      "method" : "POST", // This is for API.
                      "auth" : "true"
                  },
                  "upload" : {
                     "url" : "/api/config/configlet/",
                      //"url" : "/configlet/",
                      "method" : "PUT",
                      //"method" : "PUT", // This is for API.
                      "auth" : "true"
                  },
                  "getById" : {
                    "url" : "/api/config/configlet/",
                      //"url" : "/configlet/",
                      "method" : "GET",
                      //"method" : "PUT", // This is for API.
                      "auth" : "true"
                  },
                  "edit" : {
                    "url" : "/api/config/configlet/",
                      //"url" : "/configlet/",
                      //"method" : "GET",
                      "method" : "PUT", // This is for API.
                      "auth" : "true"
                  },
                  "delete" : {
                    "url" : "/api/config/configlet/",
                      //"url" : "/configlet/",
                     "method" : "DELETE",
                      //"method" : "POST", // This is for API.
                     "auth" : "true"
                  }
                },
                "pools" : {
                  "list" : {
                      "url" : "/api/pool/pool",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "add" : {
                        "url" : "/api/pool/pool",
                        "method" : "POST",
                        "auth" : "true"
                    },
                    "getById" : {
                      "url" : "/api/pool/pool/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "edit" : {
                      "url" : "/api/pool/pool/",
                      "method" : "PUT",
                      "auth" : "true"
                    },
                    "delete" : {
                      "url" : "/api/pool/pool/",
                      "method" : "DELETE",
                      "auth" : "true"
                    }
                },

                "users" : {
                  "register" : {
                    "url" : "/auth/register/",
                    "method" : "POST"
                  },
                  "login" : {
                   //"url" : "/data/login.json",
                    "url" : "/auth/login/",
                    "method" : "POST"
                   // "method" : "GET", // just for test
                  },
                  "logout" : {
                    "url" : "/auth/logout/",
                    "method" : "POST",
                    "auth" : "true"
                  },
                },
                "workflow" : {
                    "list" : {
                        "url" : "/api/workflow/workflow",
                        "method" : "GET",
                        "auth" : "true"
                    },
                    "add" : {
                        "url" : "/api/workflow/workflow",
                        "method" : "POST",
                        "auth" : "true"
                    },
                    "getById" : {
                        "url" : "/api/workflow/workflow/",
                        "method" : "GET",
                        "auth" : "true"
                    },
                    "edit" : {
                        "url" : "/api/workflow/workflow/",
                        "method" : "PUT", 
                        "auth" : "true"
                    },
                    "delete" : {
                        "url" : "/api/workflow/workflow/",
                        "method" : "DELETE",
                        "auth" : "true"
                    }
                },
                "task" : {
                    "list" : {
                        "url" : "/api/workflow/task",
                        "method" : "GET",
                        "auth" : "true"
                    },
                    "add" : {
                        "url" : "/api/workflow/task",
                        "method" : "POST",
                        "auth" : "true"
                    },
                    "getById" : {
                        "url" : "/api/workflow/task/",
                        "method" : "GET",
                        "auth" : "true"
                    },
                    "edit" : {
                        "url" : "/api/workflow/task/",
                        "method" : "PUT", 
                        "auth" : "true"
                    },
                    "delete" : {
                        "url" : "/api/workflow/task/",
                        "method" : "DELETE",
                        "auth" : "true"
                    }
                },

                "topology": {
                    "list": {
                        "url": "/api/fabric/topology",
                        "method": "GET",
                        "auth": "true"
                    },
                    "defaults" : {
                      "url" : "/api/fabric/topology/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "create" : {
                      "url": "/api/fabric/topology",
                      "method": "POST",
                      "auth": "true"
                    },
                    "add_switch_Link" : {
                      "url": "/api/fabric/topology/",
                      "method": "POST",
                      "auth": "true"
                    },
                    "clone" : {
                      "url": "/api/fabric/topology/",
                      "method": "POST",
                      "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/fabric/topology/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "getById" : {
                      "url" : "/api/fabric/topology/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "item": {
                        "url": "/data/topology1.json",
                        "method": "GET",
                        "auth": "false"
                    },
                    "delete" : {
                        "url" : "/api/fabric/topology/",
                        "method" : "DELETE",
                        "auth" : "true"
                      },
                },
                "configuration": {
                    "list": {
                        "url": "/api/config/profile",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
                        "url": "/api/config/profile",
                        "method": "POST",
                        "auth": "true"
                    },
                    "view" : {
                        "url": "/api/config/profile/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/config/profile/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "delete" : {
                        "url": "/api/config/profile/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },

                "discoveryRule" : {
                    "list": {
                        "url": "/api/discovery/rule",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add": {
                        "url": "/api/discovery/rule",
                        "method": "POST",
                        "auth": "true"
                    },
                    "edit": {
                        "url": "/api/discovery/rule/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "getById" : {
                      "url" : "/api/discovery/rule/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "delete" : {
                        "url": "/api/discovery/rule/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },
                "fabricInstance" : {
                    "list": {
                        "url": "/api/fabric/fabric",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add": {
                        "url": "/api/fabric/fabric",
                        "method": "POST",
                        "auth": "true"
                    },
                    "clone" : {
                      "url": "/api/fabric/fabric/",
                      "method": "POST",
                      "auth": "true"
                    },
                    "edit": {
                        "url": "/api/fabric/fabric/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "getById" : {
                      "url" : "/api/fabric/fabric/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "delete" : {
                        "url": "/api/fabric/fabric/",
                        "method": "DELETE",
                        "auth": "true"
                    },
                    "buildConfig" : {
                      "url": "/api/fabric/fabric/",
                      "method": "PUT",
                      "auth": "true"
                    },
                    "add_switch_Link" : {
                      "url": "/api/fabric/fabric/",
                      "method": "POST",
                      "auth": "true"
                    }
                },
                "deployedFabrics" : {
                    "list": {
                        "url": "/api/fabric/deployed",
                        "method": "GET",
                        "auth": "true"
                    },
                    "replicaDetails": {
                        "url": "/api/fabric/deployed/",
                        "method": "GET",
                        "auth": "true"
                    },

                    "getConfig": {
                        "url": "/api/fabric/deployed/config/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "getLog": {
                        "url": "/api/fabric/deployed/logs/",
                        "method": "GET",
                        "auth": "true"
                    }
                },
                'deployedSwitches' : {
                  "list": {
                        "url": "/api/bootstrap/booted",
                        "method": "GET",
                        "auth": "true"
                  },
                  "view_config": {
                        "url": "/api/bootstrap/config/",
                        "method": "GET",
                        "auth": "true"
                  },
                  "view_log": {
                        "url": "/api/bootstrap/logs/",
                        "method": "GET",
                        "auth": "true"
                  }
                },
                "images" : {
                    "list" : {
                      "url": "/api/image/profile",
                      "method": "GET",
                      "auth": "true"
                    },
                    "add" : {
                      "url": "/api/image/profile",
                      "method": "POST",
                      "auth": "true"
                    },
                    "getById" : {
                      "url": "/api/image/profile/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "edit" : {
                      "url": "/api/image/profile/",
                      "method": "PUT",
                      "auth": "true"
                    },
                    "delete" : {
                      "url": "/api/image/profile/",
                      "method": "DELETE",
                      "auth": "true"
                    }
                },
                "linecard" : {
                  "list" : {
                      "url": "/api/switch/linecard",
                      "method": "GET",
                      "auth": "true"
                    },
                  "add" : {
                      "url": "/api/switch/linecard",
                      "method": "POST",
                      "auth": "true"
                    },
                  "getById" : {
                      "url": "/api/switch/linecard/",
                      "method": "GET",
                      "auth": "true"
                    },
                  "edit" : {
                      "url": "/api/switch/linecard/",
                      "method": "PUT",
                      "auth": "true"
                    },
                  "delete" : {
                      "url": "/api/switch/linecard/",
                      "method": "DELETE",
                      "auth": "true"
                    }
                },
                "switches" : {
                  "list" : {
                      "url": "/api/switch/model",
                      "method": "GET",
                      "auth": "true"
                    },
                  "add" : {
                      "url": "/api/switch/model",
                      "method": "POST",
                      "auth": "true"
                    },
                  "getById" : {
                      "url": "/api/switch/model/",
                      "method": "GET",
                      "auth": "true"
                    },
                  "edit" : {
                      "url": "/api/switch/model/",
                      "method": "PUT",
                      "auth": "true"
                    },
                  "delete" : {
                      "url": "/api/switch/model/",
                      "method": "DELETE",
                      "auth": "true"
                    }
                },
                "profileTemplates" : {
                    "list" : {
                        "url" : "/api/feature/feature",
                        "method" : "GET",
                        "auth" : "true"
                      },
                    "add" : {
                        "url" : "/api/feature/feature",
                        "method" : "POST",
                        "auth" : "true"
                    },
                    "upload" : {
                       "url" : "/api/feature/feature/",
                        "method" : "PUT",
                        "auth" : "true"
                    },
                    "getById" : {
                      "url" : "/api/feature/feature/",
                        "method" : "GET",
                        "auth" : "true"
                    },
                    "edit" : {
                      "url" : "/api/feature/feature/",
                        "method" : "PUT", 
                        "auth" : "true"
                    },
                    "delete" : {
                      "url" : "/api/feature/feature/",
                       "method" : "DELETE",
                       "auth" : "true"
                    }
                },
                "fabricProfile" : {
                    "list": {
                        "url": "/api/feature/profile",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
                        "url": "/api/feature/profile",
                        "method": "POST",
                        "auth": "true"
                    },
                    "view" : {
                        "url": "/api/feature/profile/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/feature/profile/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "delete" : {
                        "url": "/api/feature/profile/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },
                "aaa_server" : {
                    "list" : {
                        "url": "/api/admin/aaa/server",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
                        "url": "/api/admin/aaa/server",
                        "method": "POST",
                        "auth": "true"
                    },
                    "view" : {
                        "url": "/api/admin/aaa/server/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/admin/aaa/server/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "delete" : {
                        "url": "/api/admin/aaa/server/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },
              "aaa_user" : {
                    "list" : {
                        "url": "/api/admin/aaa/user",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
                        "url": "/api/admin/aaa/user",
                        "method": "POST",
                        "auth": "true"
                    },
                    "view" : {
                        "url": "/api/admin/aaa/user/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/admin/aaa/user/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "delete" : {
                        "url": "/api/admin/aaa/user/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },
              "rma" : {
                    "search" : {
                      "url": "/api/bootstrap/rma/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "replace" : {
                      "url": "/api/bootstrap/rma/rma",
                      "method": "POST",
                      "auth": "true"
                    }
                },
              "backup" : {
                    "list" : {
                      "url": "/api/admin/backup",
                      "method": "GET",
                      "auth": "true"
                    },
                    "add": {
                      "url": "/api/admin/backup",
                      "method": "POST",
                      "auth": "true"
                    },
                    "delete": {
                      "url": "/api/admin/backup",
                      "method": "DELETE",
                      "auth": "true"
                    },
                    "download": {
                      "url": "/api/admin/backup/",
                      "method": "GET",
                      "auth": "true"
                    }
              },
              "group" : {
                    "list" : {
                      "url": "/api/manage/group",
                      "method": "GET",
                      "auth": "true"
                    },
                    "create": {
                      "url": "/api/manage/group",
                      "method": "POST",
                      "auth": "true"
                    },
                    "getById": {
                      "url": "/api/manage/group/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "addSwitches": {
                      "url": "/api/manage/group/",
                      "method": "POST",
                      "auth": "true"
                    },
                    "edit": {
                      "url": "/api/manage/group/",
                      "method": "PUT",
                      "auth": "true"
                    },
                    "getGrpSwitch": {
                      "url": "/api/manage/group/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "delete": {
                      "url": "/api/manage/group/",
                      "method": "DELETE",
                      "auth": "true"
                    }
              },
              "job" : {
                    "list": {
                      "url": "/api/manage/job",
                      "method": "GET",
                      "auth": "true"
                    },
                    "add": {
                      "url": "/api/manage/job",
                      "method": "POST",
                      "auth": "true"
                    },
                    "getById": {
                      "url": "/api/manage/job/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "edit": {
                      "url": "/api/manage/job/",
                      "method": "PUT",
                      "auth": "true"
                    },
                    "delete": {
                      "url": "/api/manage/job/",
                      "method": "DELETE",
                      "auth": "true"
                    }
              }
            },
            "dateFormat": 'dd/MMM/yyyy hh:mm:ss a',
            "dateFormat-short": 'dd/MMM/yyyy',
            "timeFormat": 'hh:mm:ss a',
            "fieldValues": {
                "configlets": {
                    "types": [{
                        "value": "configlet",
                        "label": "Template"
                    }, {
                        "value": "script",
                        "label": "Script"
                    }]
                },
                "pools" : {
                  "types" : [
                    {
                      "value" : "IPv4",
                      "label" : "IPv4"
                    },
                    {
                      "value" : "IPv6",
                      "label" : "IPv6"
                    },
                    {
                      "value" : "Integer",
                      "label" : "Integer"
                    }
                  ],
                  "scopes" : [
                    {
                      "value" : "Global",
                      "label" : "Global"
                    },
                    {
                      "value" : "Fabric",
                      "label" : "Fabric"
                    }
                  ],
                  "roles" : [
                    {
                      "value" : "Mgmt",
                      "label" : "Mgmt"
                    }
                  ]
                },
                'construct' : {
                  "types" : [{
                      "value" : "append_configlet",
                      "label" : "Append configlet"
                    },{
                      "value" : "append_script",
                      "label" : "Append script"
                  }],
                  'paramTypes' : [{
                      "value" : "Fixed",
                      "label" : "Fixed"
                    },{
                      "value" : "Instance",
                      "label" : "Instance"
                    },{
                      "value" : "Pool",
                      "label" : "Pool"
                    },{
                      "value" : "Value",
                      "label" : "Value"
                    },{
                      "value" : "Eval",
                      "label" : "Evaluate"
                    }
                  ],
                  'instanceTypes' : [{
                      "value" : "HOST_NAME",
                      "label" : "HOST_NAME"
                    },
                    {
                      "value" : "VPC_PEER_SRC",
                      "label" : "VPC_PEER_SRC"
                    },
                    {
                      "value" : "VPC_PEER_DST",
                      "label" : "VPC_PEER_DST"
                    },
                    {
                      "value" : "VPC_PEER_PORTS",
                      "label" : "VPC_PEER_PORTS"
                    },
                    {
                      "value" : "UPLINK_PORTS",
                      "label" : "UPLINK_PORTS"
                    },
                    {
                      "value" : "DOWNLINK_PORTS",
                      "label" : "DOWNLINK_PORTS"
                    }
                  ]
                },
                'fabricConstruct' : {
                    "types" : [{
                      "value" : "append_template",
                      "label" : "Append Template"
                    }],
                    'paramTypes' : [{
                      "value" : "Fixed",
                      "label" : "Fixed"
                    }]
                },
                'discoveryRule' : {
                  "rnConditions" : [
                    {
                      "value" : "contain",
                      "label" : "contain"
                    },
                    {
                      "value" : "no_contain",
                      "label" : "no_contain"
                    },
                    {
                      "value" : "match",
                      "label" : "match"
                    },
                    {
                      "value" : "no_match",
                      "label" : "no_match"
                    },
                    {
                      "value" : "any",
                      "label" : "any"
                    }
                  ],
                  "rpConditions" : [
                    {
                      "value" : "contain",
                      "label" : "contain"
                    },
                    {
                      "value" : "no_contain",
                      "label" : "no_contain"
                    },
                    {
                      "value" : "match",
                      "label" : "match"
                    },
                    {
                      "value" : "no_match",
                      "label" : "no_match"
                    },
                    {
                      "value" : "any",
                      "label" : "any"
                    }
                  ],
                  "lpConditions" : [
                    {
                      "value" : "contain",
                      "label" : "contain"
                    },
                    {
                      "value" : "no_contain",
                      "label" : "no_contain"
                    },
                    {
                      "value" : "match",
                      "label" : "match"
                    },
                    {
                      "value" : "no_match",
                      "label" : "no_match"
                    },
                    {
                      "value" : "any",
                      "label" : "any"
                    }
                  ]
                },
                "aaa" : {
                  "protocols" : [
                    {
                      "value" : "radius",
                      "label" : "RADIUS"
                    },
                    {
                      "value" : "tacacs+",
                      "label" : "TACACS+"
                    }
                  ]
                },
                "users" : {
                  "roles" : [
                    {
                      "value" : "Network-Admin",
                      "label" : "Network-Admin"
                    },
                    {
                      "value" : "Network-Operator",
                      "label" : "Network-Operator"
                    }
                  ]
                },
                "jobs" : {
                  "upgrade_type" : [
                    {
                      "value" : "switch_upgrade",
                      "label" : "Switch Upgrade"
                    },
                    {
                      "value" : "epld_upgrade",
                      "label" : "EPLD Upgrade"
                    }
                  ],
                  "failure_actions" : [
                    {
                      "value" : "continue",
                      "label" : "continue"
                    },
                    {
                      "value" : "abort",
                      "label" : "abort"
                    }
                  ]
                }
            },
            "defaultData": {
                "configlets": {
                    "config_type": "configlet"
                },
                "jobs": {
                    "failure_action": "continue"
                },
                "images": {
                    "access_protocol": "scp"
                },
                "switches": {
                  "port_speed": "1/10G",
                  "transceiver": "GBASE-T",
                  "port_role": "Both"
                },
                "pools" : {
                    "scope" : "Global"
                },
                "discoveryRule" : {
                    "rnCondition" : "match",
                    "rpCondition" : "match",
                    "lpCondition" : "match",
                    "match" : "all",
                    "buildConfigurationId" : "",
                    "priority" : 1
                }
            },
            "tableSettings" : {
               "count" : 10
            },
            "errorMsg" : {
              "duplicateName" : "Duplicate name. Choose another name.",
              "numberOutOfRange" : "Number out of range."
            }

        })
}());
