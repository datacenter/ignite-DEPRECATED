angular.module('topologyModule', [])

.config(['$logProvider', function($logProvider) {
    $logProvider.debugEnabled(true);
}])

.directive('topologyViewer', ['appSettings', function (appSettings) {

    return {
        restrict: 'E',
        scope:{
          topology: '=',
          prefix: '='
        },
        link: function (scope, iElement, iAttrs) {
          scope.$watch('prefix', function(newValue, oldValue) {
              if (newValue !== oldValue) {
                // Logic
                console.log("I got the new value! ", newValue);
              }
          }, true);
        },
        controller : function($scope) {
          console.log('Inside Link ::');
          console.log($scope.topology);

          var preFixedTopology = angular.copy($scope.topology);
          var prefix = $scope.prefix;
          console.log('Prefix : ' + prefix);

          //Core
          for(var i=0; i<preFixedTopology.topology_json.core_list.length;i++){
              preFixedTopology.topology_json.core_list[i].name = prefix + '-' + preFixedTopology.topology_json.core_list[i].name;
          }

          //Spine
          for(var i=0; i<preFixedTopology.topology_json.spine_list.length;i++){
              preFixedTopology.topology_json.spine_list[i].name = prefix + '-' + preFixedTopology.topology_json.spine_list[i].name;
          }

          //Leaf
          for(var i=0; i<preFixedTopology.topology_json.leaf_list.length;i++){
              preFixedTopology.topology_json.leaf_list[i].name = prefix + '-' + preFixedTopology.topology_json.leaf_list[i].name;
          }

          //Host
          if(typeof preFixedTopology.topology_json.host_list !='undefined')
          for(var i=0; i<preFixedTopology.topology_json.host_list.length;i++){
              preFixedTopology.topology_json.host_list[i].name = prefix + '-' + preFixedTopology.topology_json.host_list[i].name;
          }

          //Link List
          for(var i=0; i<preFixedTopology.topology_json.link_list.length;i++){
              preFixedTopology.topology_json.link_list[i].switch_1 = prefix + '-' + preFixedTopology.topology_json.link_list[i].switch_1;
              preFixedTopology.topology_json.link_list[i].switch_2 = prefix + '-' + preFixedTopology.topology_json.link_list[i].switch_2;
          }

          $scope.topology = preFixedTopology;
          console.log(preFixedTopology);
        },
        templateUrl: 'scripts/modules/topology_viewer.html'
    };
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

.controller('TopologyViewerCtrl', function($scope, $log, $http, $filter) {
  console.log($scope.prefix);
  console.log('-------*-*-*-*-*-*-*--*-*----------------------')
  console.log($scope.topology);

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

    //Apply the code the viewer
    $scope.topologyData = angular.copy($scope.topology);
    $scope.action = 'view';
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

    $scope.PopEdit = function(id){
      PopEdit(id);
    }

    $scope.PopEditLink = function(id){
      PopEditLink(id);
    }

    /*Initialize the topology*/
    $scope.init = function() {

        $("button").tooltip({
            'container': 'body',
            'placement': 'top'
        });

        $log.debug('Initial Topology Object by creating a copy of the data got from JSON');
        $log.debug($scope.topology);
        $scope.topology = angular.copy($scope.topologyData);
        setTopologyData($scope.topology);
    }
    $scope.init();
    // $scope.addLinkModal();

});
