angular.module('topologyApp', [])

.config(['$logProvider', function($logProvider) {
    $logProvider.debugEnabled(true);
}])



.filter('filter_link', function() {
    return function(linkTypes, applicableTo) {

        linkTypeFiltered = [];


        for (i = 0; i < linkTypes.length; i++) {
            for (j = 0; j < linkTypes[i].link_combo.length; j++) {
                if (applicableTo[0].indexOf(linkTypes[i].link_combo[j][0]) > -1 && applicableTo[1].indexOf(linkTypes[i].link_combo[j][1]) > -1) {
                    linkTypeFiltered.push(linkTypes[i]);
                }
            }
        }
        return linkTypeFiltered;
    }
})


.controller('TopologyCtrl', function($scope, $log, $http, $filter) {

    $scope.maxCore = 4;
    $scope.maxSpine = 8;
    $scope.maxLeaf = 192;
    $scope.maxHost = 1000;

    //Empty Topology Structuref
    $scope.topologyStructure = {
        "name": "",
        "submit": "false",
        "topology_json": {
            "core_list": [],
            "spine_list": [],
            "leaf_list": [],
            "host_list": [],
            "link_list": []
        }
    }

    //Default Core Structure
    $scope.coreStructure = {
        "id": "core",
        "name": "Core",
        "type": "BGPCore"
    }

    //Default Spine Structure
    $scope.spineStructure = {
        "id": "spine",
        "name": "Spine",
        "type": "NX9504"
    };

    //Default Leaf Structure
    $scope.leafStructure = {
        "id": "leaf",
        "name": "Leaf",
        "type": "Leaf48+6"
    };

    //Host or other Structure - naming it host for now till name is provided
    $scope.hostStructure = {
        "id": "host",
        "name": "Host",
        "type": "Host1",
    };

    //Default Link Structure
    $scope.linkStructure = {
        "id_2": "",
        "switch_2": "",
        "port_list_2": [""],
        "id_1": "",
        "switch_1": "",
        "port_list_1": [""],
        "link_type": ""
    };

    //Default types and link combinations
    $scope.coreTypes = ["BGPCore"];
    $scope.spineTypes = ["NX9504", "NX9508", "NX9516"];
    $scope.leafTypes = ["NX9332PQ", "NX9372PX", "NX9372TX", "NX9396PX", "NX9396TX", "NX93120TX", "NX93128TX"];
    $scope.hostTypes = ["Host1", "Host2"];
    $scope.linkTypes = [{
            "link_group": "Linkset",
            "link_type": "Linkset-1Link",
            "link_ports": 1,
            "link_combo": [
                ["core", "spine"],
                ["spine", "leaf"],
                ["leaf", "host"]
            ]
        }, {
            "link_group": "Linkset",
            "link_type": "Linkset-2Link",
            "link_ports": 2,
            "link_combo": [
                ["core", "spine"],
                ["spine", "leaf"],
                ["leaf", "host"]
            ]
        }, {
            "link_group": "Linkset",
            "link_type": "Linkset-3Link",
            "link_ports": 3,
            "link_combo": [
                ["core", "spine"],
                ["spine", "leaf"],
                ["leaf", "host"]
            ]
        }, {
            "link_group": "Linkset",
            "link_type": "Linkset-4Link",
            "link_ports": 4,
            "link_combo": [
                ["core", "spine"],
                ["spine", "leaf"],
                ["leaf", "host"]
            ]
        },

        {
            "link_group": "VPC",
            "link_type": "VPC-1Link",
            "link_ports": 1,
            "link_combo": [
                ["leaf", "leaf"]
            ]
        }, {
            "link_group": "VPC",
            "link_type": "VPC-2Link",
            "link_ports": 2,
            "link_combo": [
                ["leaf", "leaf"]
            ]
        }, {
            "link_group": "VPC",
            "link_type": "VPC-3Link",
            "link_ports": 3,
            "link_combo": [
                ["leaf", "leaf"]
            ]
        }, {
            "link_group": "VPC",
            "link_type": "VPC-4Link",
            "link_ports": 4,
            "link_combo": [
                ["leaf", "leaf"]
            ]
        },

        {
            "link_group": "PortChannel",
            "link_type": "PortChannel-1Link",
            "link_ports": 1,
            "link_combo": [
                ["leaf", "host"]
            ]
        }, {
            "link_group": "PortChannel",
            "link_type": "PortChannel-2Link",
            "link_ports": 2,
            "link_combo": [
                ["leaf", "host"]
            ]
        }, {
            "link_group": "PortChannel",
            "link_type": "PortChannel-3Link",
            "link_ports": 3,
            "link_combo": [
                ["leaf", "host"]
            ]
        }, {
            "link_group": "PortChannel",
            "link_type": "PortChannel-4Link",
            "link_ports": 4,
            "link_combo": [
                ["leaf", "host"]
            ]
        },

        {
            "link_group": "KeepAliveLink",
            "link_type": "KeepAliveLink",
            "link_ports": 1,
            "link_combo": [
                ["leaf", "leaf"]
            ]
        }
    ];

    // Get this data through ajax
    $scope.topologyData = angular.copy($scope.topologyStructure);



    // Create a New Topology
    $scope.newTopology = function() {
        $scope.coreLeft = 0;
        $scope.spineLeft = 0;
        $scope.leafLeft = 0;
        $scope.topology = angular.copy($scope.topologyStructure);
        doReload($scope.topology);
    }

    //Revert back to saved Topology - got from ajax above
    $scope.doReset = function() {
        if (confirm('Are you sure you want to reset to last loaded data?')) {
            $scope.topology = angular.copy($scope.topologyData);
            doReload($scope.topology);
        }
    }

    //Check for changes in list items
    $scope.coreLeft = 0;
    $scope.spineLeft = 0;
    $scope.leafLeft = 0;

    $scope.$watch(function() {
        $scope.coreLeft = $scope.maxCore - $scope.topology.topology_json.core_list.length;
        $scope.spineLeft = $scope.maxSpine - $scope.topology.topology_json.spine_list.length;
        $scope.leafLeft = $scope.maxLeaf - $scope.topology.topology_json.leaf_list.length;
    })


    //NOT DONE
    $scope.notDone = function() {
        alert('Not Implemented');
    }

    /*********Auto Populate the Ports***********/

    $scope.portMaker = function(options) {
        /************************* Defaults ********************************/
        var defaults = {
            "portChar": "e",
            "portStart": 1,
            "noOfRacks": 12,
            "noOfPorts": 24
        };
        defaults.maxPorts = defaults.noOfRacks * defaults.noOfPorts;
        /************************* Defaults ********************************/

        var opts = $.extend(defaults, options);

        var portArray = [];

        for (var i = opts.portStart; i < opts.noOfRacks + 1; i++) {
            for (var j = 1; j < opts.noOfPorts + 1; j++) {
                var portName = opts.portChar + i + "/" + j;
                portArray.push(portName);
            }
        }
        return (portArray);
    }

    //Watch the ports
    $scope.corePorts = $scope.portMaker();
    $scope.spinePorts = $scope.portMaker();
    $scope.leafPorts = $scope.portMaker();
    $scope.hostPorts = $scope.portMaker();

    //exPorts = existing Ports - this is needed when you are adding more ports to a switch
    //Logic for adding more ports needs to be coded ***************************************
    $scope.corePortAutoPopulate = function(index, exPorts) {

        console.log('coreIndex=' + index);
        var switchItem = $scope.topology.topology_json.core_list[index];
        var assignPort = switchItem.ports.shift();
        console.log(switchItem);
        if (exPorts == undefined) {
            var exPorts = []
        }
        exPorts.push(assignPort);
        //debugger;
        return exPorts;
        //return ["xxx"];
    }

    $scope.spinePortAutoPopulate = function(index, exPorts) {

        console.log('spineIndex=' + index);
        var switchItem = $scope.topology.topology_json.spine_list[index];
        var assignPort = switchItem.ports.shift();
        console.log(switchItem);
        if (exPorts == undefined) {
            var exPorts = []
        }
        exPorts.push(assignPort);
        //debugger;
        return exPorts;
        // return ["xxx"];
    }

    $scope.leafPortAutoPopulate = function(index, exPorts) {
        var switchItem = $scope.topology.topology_json.leaf_list[index];
        var assignPort = switchItem.ports.shift();
        if (exPorts == undefined) {
            var exPorts = []
        }
        exPorts.push(assignPort);
        return exPorts;
    }

    $scope.hostPortAutoPopulate = function(index, exPorts) {
        var switchItem = $scope.topology.topology_json.host_list[index];
        var assignPort = switchItem.ports.shift();
        if (exPorts == undefined) {
            var exPorts = []
        }
        exPorts.push(assignPort);
        return exPorts;
    }


    //*************************************************** Adding Core ***************************************************//
    $scope.addCore = function() {
        var coreCount = $scope.topology.topology_json.core_list.length;

        if (coreCount >= $scope.maxCore) {
            $scope.modalContent = "You cannot have more than " + $scope.maxCore + " core in a topology."
            $('#myModal').modal('toggle');
        } else {
            //Add Core
            var coreStructure = angular.copy($scope.coreStructure);
            coreStructure.id = $scope.coreStructure.id + (coreCount + 1);
            coreStructure.name = $scope.coreStructure.name + (coreCount + 1);

            coreStructure.ports = angular.copy($scope.corePorts);

            $scope.topology.topology_json.core_list.splice(coreCount, 0, coreStructure);

            $log.debug('Add a core');
            $log.debug($scope.topology.topology_json.core_list);

            $scope.connectCoreToSpine(coreCount);
            doReload($scope.topology);
        }
    }

    $scope.connectCoreToSpine = function(coreCount) {
        $log.debug('Connect Core to Spine if Spine exists');

        //Connect all spines to the new Core
        if ($scope.topology.topology_json.spine_list != undefined && $scope.topology.topology_json.spine_list.length > 0) {
            for (var j = 0; j < $scope.topology.topology_json.spine_list.length; j++) {
                var linkStructure = angular.copy($scope.linkStructure);
                linkStructure.id_1 = $scope.topology.topology_json.core_list[coreCount].id;
                linkStructure.id_2 = $scope.topology.topology_json.spine_list[j].id;

                linkStructure.switch_1 = $scope.topology.topology_json.core_list[coreCount].name;
                linkStructure.switch_2 = $scope.topology.topology_json.spine_list[j].name;

                linkStructure.link_type = $scope.linkTypes[0].link_type;
                // Autopopulate the ports
                linkStructure.port_list_1 = $scope.corePortAutoPopulate(coreCount); //Core
                linkStructure.port_list_2 = $scope.spinePortAutoPopulate(j); //Spine

                $scope.topology.topology_json.link_list.push(linkStructure);
            }
        }
    }


    //*************************************************** Adding Spines *************************************************//
    $scope.addSpine = function() {
        var spineCount = $scope.topology.topology_json.spine_list.length;

        if (spineCount >= $scope.maxSpine) {
            $scope.modalContent = "You cannot have more than " + $scope.maxSpine + " spine in a topology."
            $('#myModal').modal('toggle');
        } else {

            //Adding a spine to the structure
            var spineStructure = angular.copy($scope.spineStructure);
            spineStructure.id = $scope.spineStructure.id + (spineCount + 1);
            spineStructure.name = $scope.spineStructure.name + (spineCount + 1);

            spineStructure.ports = angular.copy($scope.spinePorts);
            //debugger;
            $scope.topology.topology_json.spine_list.splice(spineCount, 0, spineStructure);



            $scope.connectSpineToLeaf(spineCount);

            $log.debug('Add a Spine');
            $log.debug($scope.topology);
            doReload($scope.topology);
        }
    }


    //Connects Spines to Leaf & Spine to Core if core is present
    $scope.connectSpineToLeaf = function(spineCount) {

        //Check if core exists
        if ($scope.topology.topology_json.core_list != undefined && $scope.topology.topology_json.core_list.length > 0) {

            //Connect new Spine to Cores
            for (var i = 0; i < $scope.topology.topology_json.core_list.length; i++) {
                var linkStructure = angular.copy($scope.linkStructure);
                linkStructure.id_1 = $scope.topology.topology_json.core_list[i].id;
                linkStructure.id_2 = $scope.topology.topology_json.spine_list[spineCount].id;

                linkStructure.switch_1 = $scope.topology.topology_json.core_list[i].name;
                linkStructure.switch_2 = $scope.topology.topology_json.spine_list[spineCount].name;

                linkStructure.link_type = $scope.linkTypes[0].link_type;

                // Autopopulate the ports
                linkStructure.port_list_1 = $scope.corePortAutoPopulate(i); //Core
                linkStructure.port_list_2 = $scope.spinePortAutoPopulate(spineCount); //Spine

                $scope.topology.topology_json.link_list.push(linkStructure);
            }
        }

        //Check if leafs exists
        if ($scope.topology.topology_json.leaf_list != undefined && $scope.topology.topology_json.leaf_list.length > 0) {

            for (var i = 0; i < $scope.topology.topology_json.leaf_list.length; i++) {
                var linkStructure = angular.copy($scope.linkStructure);
                linkStructure.id_1 = $scope.topology.topology_json.spine_list[spineCount].id;
                linkStructure.id_2 = $scope.topology.topology_json.leaf_list[i].id;

                linkStructure.switch_1 = $scope.topology.topology_json.spine_list[spineCount].name;
                linkStructure.switch_2 = $scope.topology.topology_json.leaf_list[i].name;

                linkStructure.link_type = $scope.linkTypes[0].link_type;

                // Autopopulate the ports
                linkStructure.port_list_1 = $scope.spinePortAutoPopulate(spineCount - 1); //Spine
                linkStructure.port_list_2 = $scope.leafPortAutoPopulate(i); //Leaf

                $scope.topology.topology_json.link_list.push(linkStructure);
            }
        }
    }

    //*************************************************** Adding Leaf *************************************************//
    $scope.addLeaf = function() {

        var leafCount = $scope.topology.topology_json.leaf_list.length;

        if (leafCount >= $scope.maxLeaf) {
            $scope.modalContent = "You cannot have more than " + $scope.maxLeaf + " leaf in a topology."
            $('#myModal').modal('toggle');
        } else {

            //Adding a leaf to the structure
            var leafStructure = angular.copy($scope.leafStructure);
            leafStructure.id = $scope.leafStructure.id + (leafCount + 1);
            leafStructure.name = $scope.leafStructure.name + (leafCount + 1);

            leafStructure.ports = angular.copy($scope.leafPorts);
            $scope.topology.topology_json.leaf_list.splice(leafCount, 0, leafStructure);

            $scope.connectLeafToSpine(leafCount);

            $log.debug('Add a Leaf');
            $log.debug($scope.topology);
            doReload($scope.topology);
        }
    }


    //Connects Leaf to Spines
    $scope.connectLeafToSpine = function(leafCount) {

        //Check if spine exists
        if ($scope.topology.topology_json.spine_list != undefined && $scope.topology.topology_json.spine_list.length > 0) {

            for (var i = 0; i < $scope.topology.topology_json.spine_list.length; i++) {
                var linkStructure = angular.copy($scope.linkStructure);
                linkStructure.id_1 = $scope.topology.topology_json.spine_list[i].id;
                linkStructure.id_2 = $scope.topology.topology_json.leaf_list[leafCount].id;

                linkStructure.switch_1 = $scope.topology.topology_json.spine_list[i].name;
                linkStructure.switch_2 = $scope.topology.topology_json.leaf_list[leafCount].name;

                linkStructure.link_type = $scope.linkTypes[0].link_type;

                // Autopopulate the ports
                linkStructure.port_list_1 = $scope.spinePortAutoPopulate(i); //Spine
                linkStructure.port_list_2 = $scope.leafPortAutoPopulate(leafCount); //Leaf

                $scope.topology.topology_json.link_list.push(linkStructure);
            }
        }
    }

    //Connects Leaf to Spines
    $scope.connectLeafToLeaf = function(leafCount) {

        if (leafCount > 0) {
            var leafToLeafLinkStructure = angular.copy($scope.leafToLeafLinkStructure);
            leafToLeafLinkStructure.switch_1 = "leaf" + (leafCount);
            leafToLeafLinkStructure.switch_2 = "leaf" + (leafCount + 1);
            leafToLeafLinkStructure.link_type = "VPC-2Link";

            leafToLeafLinkStructure.port_list_1 = $scope.leafPortAutoPopulate(leafCount - 1);
            leafToLeafLinkStructure.port_list_2 = $scope.leafPortAutoPopulate(leafCount - 1);

            $log.debug('**************************');
            $log.debug(leafToLeafLinkStructure);

            //Connect leaf to previous leaf
            $scope.topology.topology_json.link_list.push(leafToLeafLinkStructure);
        }
    }


    //*************************************************** Adding Host *************************************************//
    $scope.addHost = function(leaf_id, leaf_index) {

        var hostCount = $scope.topology.topology_json.host_list.length;

        if (hostCount >= $scope.maxHost) {
            $scope.modalContent = "You cannot have more than " + $scope.maxHost + " hosts in a topology."
            $('#myModal').modal('toggle');
        } else {

            //Adding a leaf to the structure
            var hostStructure = angular.copy($scope.hostStructure);
            hostStructure.id = $scope.hostStructure.id + (hostCount + 1);
            hostStructure.name = $scope.hostStructure.name + (hostCount + 1);

            hostStructure.ports = angular.copy($scope.hostPorts);
            $scope.topology.topology_json.host_list.splice(hostCount, 0, hostStructure);

            $scope.connectHostToLeaf(hostCount, leaf_id, leaf_index);

            $log.debug('Add a Host');
            $log.debug($scope.topology);
            doReload($scope.topology);
        }
    }

    //Connects Leaf to Spines
    $scope.connectHostToLeaf = function(hostCount, leaf_id, leaf_index) {

        //Check if spine exists
        if ($scope.topology.topology_json.host_list != undefined && $scope.topology.topology_json.host_list.length > 0) {

            var linkStructure = angular.copy($scope.linkStructure);
            linkStructure.id_1 = $scope.topology.topology_json.leaf_list[leaf_index].id;
            linkStructure.id_2 = $scope.topology.topology_json.host_list[hostCount].id;

            linkStructure.switch_1 = $scope.topology.topology_json.leaf_list[leaf_index].name;
            linkStructure.switch_2 = $scope.topology.topology_json.host_list[hostCount].name;

            linkStructure.link_type = $scope.linkTypes[0].link_type;

            // Autopopulate the ports
            linkStructure.port_list_1 = $scope.leafPortAutoPopulate(leaf_index); //Leaf
            linkStructure.port_list_2 = $scope.hostPortAutoPopulate(hostCount); //Host

            $scope.topology.topology_json.link_list.push(linkStructure);
        }
    }

    /*Update Port Entry based on Link type*/
    $scope.updatePortsByLinkType = function(link) {
        $log.debug('updatePortsByLinkType');
        $log.debug(link);

        for (var j = 0; j < $scope.linkTypes.length; j++) {
            if ($scope.linkTypes[j].link_type == link.link_type) {

                $log.debug(j + " $scope.linkTypes[j].link_type == link.link_type" + $scope.linkTypes[j].link_type + "==" + link.link_type + " # port=" + $scope.linkTypes[j].link_ports)

                link.port_list_1 = [];
                link.port_list_2 = [];

                for (var k = 0; k < $scope.linkTypes[j].link_ports; k++) {
                    $log.debug('in here');
                    link.port_list_1.push("x" + k);
                    link.port_list_2.push("x" + k);
                }
                break;
            }
        }
    }

    /************************* Save Reload ***********************/

    $scope.saveReload = function(list, id, index) {

        //Update Link list names
        for (var i = 0; i < $scope.topology.topology_json.link_list.length; i++) {

            if ($scope.topology.topology_json.link_list[i].id_1 == id) {
                $scope.topology.topology_json.link_list[i].switch_1 = list[index].name;
            }
            if ($scope.topology.topology_json.link_list[i].id_2 == id) {
                $scope.topology.topology_json.link_list[i].switch_2 = list[index].name;
            }

        }
        saveReloadTopology($scope.topology);
    }


    /*********************** Delete Item ***********************/
    $scope.toDeleteItem = 0;
    $scope.toDeleteList = "";

    $scope.deleteItem = function(topologyList, item, itemName) {
        $('#popEdit').hide();
        $('#popEdit_Item_' + itemID).hide();
        $('#popEditLink_Item_' + itemLinkID).hide();

        $('#modalDeleteContent').html('Are you sure you want to delete ' + itemName + "?");
        $('#myModalDelete').modal('toggle');

        $scope.toDeleteItem = item;
        $scope.toDeleteList = topologyList;

        console.log("toDeleteItem=" + $scope.toDeleteItem);
    }

    /************************* Delete Switch ***********************/

    $scope.deleteSwitch = function() {

        if ($scope.toDeleteItem == 0) {
            alert('Sorry, nothing to delete');
        } else {
            //Splice the link list backward
            var i = $scope.topology.topology_json.link_list.length;

            while (i--) {
                if ($scope.topology.topology_json.link_list[i].id_1 == $scope.toDeleteItem || $scope.topology.topology_json.link_list[i].id_2 == $scope.toDeleteItem) {
                    $scope.topology.topology_json.link_list.splice(i, 1);
                }
            }


            if ($scope.toDeleteList == "") {
                alert('Sorry, nothing to delete');
            } else {

                switch ($scope.toDeleteList) {
                    case 'core':
                        list = $scope.topology.topology_json.core_list;
                        break;
                    case 'spine':
                        list = $scope.topology.topology_json.spine_list;
                        break;
                    case 'leaf':
                        list = $scope.topology.topology_json.leaf_list;
                        break;
                    case 'host':
                        list = $scope.topology.topology_json.host_list;
                        break;
                    default:
                        //
                }

                var i = list.length;

                while (i--) {
                    if (list[i].id == $scope.toDeleteItem) {
                        list.splice(i, 1);
                    }
                }
            }

            $log.debug('Deleting switch from switch list & its corresponding links from link list');
            $log.debug($scope.topology);

            doReload($scope.topology);
        }
    }


    /**************Add Link ******************************/

    $scope.addLinkModal = function(linkFor) {

        $scope.linkFor = linkFor;
        $('#myModalLink').modal('toggle');
    }

    $scope.checkLinkExists = function(switch1, switch2) {


        $log.debug('switch1 and switch2');
        console.log(switch1);
        console.log(switch2);

        if (switch1 != undefined && switch2 != undefined) {

            if (switch1 == switch2) {
                $('#alertLinkSame').show()
            } else {
                $('#alertLinkSame').hide()
            }

            for (var i = 0; i < $scope.topology.topology_json.link_list.length; i++) {

                if (($scope.topology.topology_json.link_list[i].id_1 == switch1.id && $scope.topology.topology_json.link_list[i].id_2 == switch2.id) || ($scope.topology.topology_json.link_list[i].id_2 == switch1.id && $scope.topology.topology_json.link_list[i].id_1 == switch2.id)) {
                    $('#alertLinkExists').show();
                    return false;
                } else {
                    $('#alertLinkExists').hide();
                }
            }
        } else {
            $('#alertLinkExists').hide();
            return false;
        }

        return true;
    }



    $scope.addLink = function(switch_1, switch_2) {
        $('#myModalLink').modal('toggle');

        var linkStructure = angular.copy($scope.linkStructure);
        linkStructure.id_1 = switch_1.id;
        linkStructure.id_2 = switch_2.id;

        linkStructure.switch_1 = switch_1.name;
        linkStructure.switch_2 = switch_2.name;

        linkStructure.link_type = $scope.linkTypes[4].link_type;

        console.log(linkStructure);

        $scope.topology.topology_json.link_list.push(linkStructure);

        doReload($scope.topology);
    }

    /************************* Remove Item Link by removing its type if both are leaf *********************/

    $scope.removeItemLinkType = function(item) {

        if (($scope.topology.topology_json.link_list[item].switch_1.indexOf('leaf') > -1 || $scope.topology.topology_json.link_list[item].switch_2.indexOf('leaf') > -1) && ($scope.topology.topology_json.link_list[item].switch_1.indexOf('spine') > -1 || $scope.topology.topology_json.link_list[item].switch_2.indexOf('spine') > -1)) {
            //this is a leaf to spine link - should not be removed but emptied

            if (confirm('You cannot remove a link between a Spine and a Leaf. Click OK to clear the Link and Port details')) {
                $scope.topology.topology_json.link_list[item].link_type = "";
                $scope.topology.topology_json.link_list[item].port_list_1 = [];
                $scope.topology.topology_json.link_list[item].port_list_2 = [];
            }
        } else {
            $scope.topology.topology_json.link_list.splice(item, 1);
        }


        doReload($scope.topology);
    }

    $scope.toggleDetailsModel = true;

    $scope.toggleDetails = function() {

        if ($scope.toggleDetailsModel) {
            document.getElementById('popEdit').style.right = "25%";
            document.getElementById('popEditLink').style.right = "25%";

            document.getElementById('topology_container').className = "col-sm-9";
        } else {
            document.getElementById('popEdit').style.right = "0%";
            document.getElementById('popEditLink').style.right = "0%";
            document.getElementById('topology_container').className = "col-sm-12";
        }

    }


    /*Initialize the topology*/
    $scope.init = function() {
        $log.debug('Initial Topology Object by creating a copy of the data got from JSON');
        $log.debug($scope.topology);
        $scope.topology = angular.copy($scope.topologyData);
        setTopologyData($scope.topology);
    }
    $scope.init();
    // $scope.addLinkModal();

});
