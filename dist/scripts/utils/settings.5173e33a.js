(function() {
    'use strict';

    /**
     * @ngdoc overview
     * @name clmServiceRequestApp Settings.js
     * @description
     * # clmServiceRequestApp
     *
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
                      "url" : "/api/configuration/configlet/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                  "add" : {
                      //"url" : "/data/add-configlets.json",
                      "url" : "/api/configuration/configlet/",
                      //"method" : "GET",
                      "method" : "POST", // This is for API.
                      "auth" : "true"
                  },
                  "upload" : {
                     "url" : "/api/configuration/configlet/",
                      //"url" : "/configlet/",
                      "method" : "PUT",
                      //"method" : "PUT", // This is for API.
                      "auth" : "true"
                  },
                  "getById" : {
                    "url" : "/api/configuration/configlet/",
                      //"url" : "/configlet/",
                      "method" : "GET",
                      //"method" : "PUT", // This is for API.
                      "auth" : "true"
                  },
                  "edit" : {
                    "url" : "/api/configuration/configlet/",
                      //"url" : "/configlet/",
                      //"method" : "GET",
                      "method" : "PUT", // This is for API.
                      "auth" : "true"
                  },
                  "delete" : {
                    "url" : "/api/configuration/configlet/",
                      //"url" : "/configlet/",
                     "method" : "DELETE",
                      //"method" : "POST", // This is for API.
                     "auth" : "true"
                  }
                },
                "pools" : {
                  "list" : {
                      "url" : "/api/pool/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "add" : {
                        "url" : "/api/pool/",
                        "method" : "POST",
                        "auth" : "true"
                    },
                    "getById" : {
                      "url" : "/api/pool/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "edit" : {
                      "url" : "/api/pool/",
                      "method" : "PUT",
                      "auth" : "true"
                    },
                    "delete" : {
                      "url" : "/api/pool/",
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
                    "method" : "POST",
                   // "method" : "GET", // just for test
                  }
                },

                "topology": {
                    "list": {
                        "url": "/api/fabric/topology/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
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
                        "url": "/api/configuration/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
                        "url": "/api/configuration/",
                        "method": "POST",
                        "auth": "true"
                    },
                    "view" : {
                        "url": "/api/configuration/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/configuration/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "delete" : {
                        "url": "/api/configuration/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },

                "discoveryRule" : {
                    "list": {
                        "url": "/api/discoveryrule/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add": {
                        "url": "/api/discoveryrule/",
                        "method": "POST",
                        "auth": "true"
                    },
                    "edit": {
                        "url": "/api/discoveryrule/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "getById" : {
                      "url" : "/api/discoveryrule/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "delete" : {
                        "url": "/api/discoveryrule/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                },
                "fabricInstance" : {
                    "list": {
                        "url": "/api/fabric/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add": {
                        "url": "/api/fabric/",
                        "method": "POST",
                        "auth": "true"
                    },
                    "edit": {
                        "url": "/api/fabric/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "getById" : {
                      "url" : "/api/fabric/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "delete" : {
                        "url": "/api/fabric/",
                        "method": "DELETE",
                        "auth": "true"
                    },
                    "buildConfig" : {
                      "url": "/api/fabric/",
                      "method": "PUT",
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
                        "url": "/api/discoveryrule/deployed",
                        "method": "GET",
                        "auth": "true"
                  }
                },
                "images" : {
                    "list" : {
                      "url": "/api/image_profile/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "add" : {
                      "url": "/api/image_profile/",
                      "method": "POST",
                      "auth": "true"
                    },
                    "getById" : {
                      "url": "/api/image_profile/",
                      "method": "GET",
                      "auth": "true"
                    },
                    "edit" : {
                      "url": "/api/image_profile/",
                      "method": "PUT",
                      "auth": "true"
                    },
                    "delete" : {
                      "url": "/api/image_profile/",
                      "method": "DELETE",
                      "auth": "true"
                    }
                },
                "profileTemplates" : {
                    "list" : {
                        "url" : "/api/fabric_profile/profile_template/",
                        "method" : "GET",
                        "auth" : "true"
                      },
                    "add" : {
                        "url" : "/api/fabric_profile/profile_template/",
                        "method" : "POST",
                        "auth" : "true"
                    },
                    "upload" : {
                       "url" : "/api/fabric_profile/profile_template/",
                        "method" : "PUT",
                        "auth" : "true"
                    },
                    "getById" : {
                      "url" : "/api/fabric_profile/profile_template/",
                        "method" : "GET",
                        "auth" : "true"
                    },
                    "edit" : {
                      "url" : "/api/fabric_profile/profile_template/",
                        "method" : "PUT", 
                        "auth" : "true"
                    },
                    "delete" : {
                      "url" : "/api/fabric_profile/profile_template/",
                       "method" : "DELETE",
                       "auth" : "true"
                    }
                },

                "fabricProfile" : {
                    "list": {
                        "url": "/api/fabric_profile/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "add" : {
                        "url": "/api/fabric_profile/",
                        "method": "POST",
                        "auth": "true"
                    },
                    "view" : {
                        "url": "/api/fabric_profile/",
                        "method": "GET",
                        "auth": "true"
                    },
                    "edit" : {
                        "url": "/api/fabric_profile/",
                        "method": "PUT",
                        "auth": "true"
                    },
                    "delete" : {
                        "url": "/api/fabric_profile/",
                        "method": "DELETE",
                        "auth": "true"
                    }
                }
            },
            "dateFormat": 'dd/MMM/yyyy hh:mm:ss a',
            "fieldValues": {
                "configlets": {
                    "types": [{
                        "value": "template",
                        "label": "Template"
                    }, {
                        "value": "script",
                        "label": "Script"
                    }]
                },
                "pools" : {
                  "types" : [
                    {
                      "value" : "Integer",
                      "label" : "Integer"
                    },
                    {
                      "value" : "Vlan",
                      "label" : "Vlan"
                    },
                    {
                      "value" : "IP",
                      "label" : "IP"
                    },
                    {
                      "value" : "IPv6",
                      "label" : "IPv6"
                    },
                    {
                      "value" : "MgmtIP",
                      "label" : "Mgmt IP"
                    }
                  ],
                  "scopes" : [
                    {
                      "value" : "global",
                      "label" : "global"
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
                      "value" : "Pool",
                      "label" : "Pool"
                    },{
                      "value" : "Instance",
                      "label" : "Instance"
                    },{
                      "value" : "Value",
                      "label" : "Value"
                    },{
                      "value" : "Fixed",
                      "label" : "Fixed"
                    },{
                      "value" : "Autogenerate",
                      "label" : "Autogenerate"
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
                    },
                    {
                      "value" : "oneof",
                      "label" : "oneof"
                    },
                    {
                      "value" : "none",
                      "label" : "none"
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
                    },
                    {
                      "value" : "oneof",
                      "label" : "oneof"
                    },
                    {
                      "value" : "none",
                      "label" : "none"
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
                    },
                    {
                      "value" : "oneof",
                      "label" : "oneof"
                    },
                    {
                      "value" : "none",
                      "label" : "none"
                    }
                  ]
                }

            },
            "defaultData": {
                "configlets": {
                    "config_type": "template"
                },
                "images": {
                    "access_protocol": "scp"
                },
                "pools" : {
                    "type" : "Integer",
                    "scope" : "global"
                },
                "discoveryRule" : {
                    "rnCondition" : "match",
                    "rpCondition" : "match",
                    "lpCondition" : "match",
                    "match" : "all",
                    "buildConfigurationId" : 1,
                    "priority" : 1
                },
                "topology" : {
                    "buildConfigurationId" : 1,
                    "templateId" : 12
                },
                "fabricInstance" : {
                    "buildConfigurationId" : 1,
                    "topologyId" : 47,
                    "replica" : 1,
                    "locked" : 1,
                    "validate" : 0
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
