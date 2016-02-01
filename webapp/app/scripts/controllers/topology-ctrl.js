'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('TopologyCtrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {
    appServices.setInternalAppUI($scope)
    var parent = $scope.$parent;

    $scope.totalItems = 64;
    $scope.currentPage = 4;

    $scope.maxSize = 5;
    $scope.bigTotalItems = 175;
    $scope.bigCurrentPage = 1;

    $scope.animationsEnabled = true;
    $scope.topologies = [];

    $scope.animationsEnabled = true;

    $scope.tableParams = new ngTableParams({
      page: 1,
      count: appSettings.tableSettings.count,
      sorting: {
        "name": "asc"
      },
      filter: {
        name: $scope.searchKeyword
      }
    }, {
      counts: [],
      getData: function($defer, params) {
        appServices.tablePagination($defer, $filter, params, $scope.topologies, $scope.searchKeyword);
      }
    });

    $scope.$watch("searchKeyword", function() {
      $scope.tableParams.reload();
      $scope.tableParams.page(1);
    });

    $scope.setPage = function(pageNo) {
      $scope.currentPage = pageNo;
    };

    $scope.pageChanged = function() {
      $log.log('Page changed to: ' + $scope.currentPage);
    };

    $scope.checkAll = function(event) {
      $scope.isChecked = $(event.toElement).is(':checked');
    };

    $scope.toggleAnimation = function() {
      $scope.animationsEnabled = !$scope.animationsEnabled;
    };

    //Fetch Topology Details
    $scope.getTopologyList = function() {
      appServices.doAPIRequest(appSettings.appAPI.topology.list, null, null).then(function(data) {
        $scope.topologies = data;
        $scope.totalTopologies = $scope.topologies.length;
        $scope.tableParams.reload();
      });
    };

    $scope.deleteTopology = function(id, $index) {
        $scope.selectedId = id;

        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        id: $scope.selectedId,
                        action: 'delete',
                        message: 'Are you sure you want to delete the topology?',
                        callerScope: $scope
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
            $scope.submitData(modalData);
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
        $scope.init();
    };

    $scope.cloneTopology = function(id) {
      $scope.action = "clone";
      $scope.selectedId = id;
      $scope.openCloneModal();
    };

    $scope.createTopo = function() {
      $scope.action = "add";
      $scope.selectedId = null;
      $scope.openCreateModal();
    };

    $scope.openCreateModal = function() {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/createTopologyModal.html',
                controller: 'TopologyCreateCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : $scope.action,
                            callerScope : $scope
                        }
                    }
                 }
            });
            $scope.modalInstance.result.then(function(modalData) {
                $scope.submitData(modalData);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

    $scope.openCloneModal = function(size) {console.log('Inside Open Clone');
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/cloneModal.html',
            controller: 'TopologyCloneModalCtrl',
            size: 'sm',
            resolve: {
                dataToModal : function() {
                    return {
                        action : $scope.action,
                        id : $scope.selectedId
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
            $scope.submitData(modalData);
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });

    };

    $scope.submitData = function(modalData) {
        if(modalData.action == 'create'){
          debugger;
          var dataToSubmit = modalData.submitData;
          appServices.doAPIRequest(appSettings.appAPI.topology.create, dataToSubmit, null).then(function(data) {
                /*localStorage.topologyId = JSON.stringify(data.id);
                localStorage.source = 'topology';*/
                $location.path('/topology/edit/'+data.id);
                /*$location.path('/topology/add/new');*/
            });
        } else if(modalData.action == 'delete') {

            var reqHeader = {
                appendToURL : true,
                value : $scope.selectedId,
                noTrailingSlash : true
            };

            appServices.doAPIRequest(appSettings.appAPI.topology.delete, null, reqHeader).then(function(data) {
                /* TODO after delete success */
                ngToast.create({
                  className: 'success',
                  content: 'Topology Deleted Successfully.'
                });
                $scope.init('delete');
            });
        }
        else if (modalData.action == 'clone') {
          var dataToSubmit = modalData.submitData;
          var requestHeader = {
            appendToURL: true,
            /* TODO - change to true in server */
            value: $scope.selectedId,
            noTrailingSlash: true
          };
          appServices.doAPIRequest(appSettings.appAPI.topology.getById, null, requestHeader).then(function(data) {
            $log.debug('Data Fetched for Topology Id : ' + $scope.selectedId);
            $log.debug(data);
            var newTopology = angular.copy(data);$log.debug('DATA::');$log.debug(data);
            newTopology.id = '';
            newTopology.name = modalData.submitData.NewCloneName;$log.debug('New To[po]');$log.debug(newTopology);
            newTopology.submit = "false";
            appServices.doAPIRequest(appSettings.appAPI.topology.add, newTopology, null).then(function(data) {
                /* TODO after delete success */
                ngToast.create({
                  className: 'success',
                  content: 'Topology Cloned Successfully.'
                });
                $scope.init('cloned');
            });
          });
        }
    };

    $scope.init = function() {
      $scope.getTopologyList();
    };


    $scope.init();
  });

  angular.module('PoapServer').controller('TopologyCloneModalCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {

    $scope.action = dataToModal.action;
    $scope.id = dataToModal.id;
    $scope.submitData = {
      "NewCloneName" : ""
    }

    $scope.ok = function() {
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            id : $scope.id
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.init = function() {};

    $scope.init();
  });

  angular.module('PoapServer').controller('TopologyCreateCtrl',
      function($scope, $modalInstance, appSettings, appServices, dataToModal){
        $scope.action = 'create';
        $scope.defaultEdit = true;
        $scope.show = {
          'Core': false,
          'Border': false
        };
        
        $scope.selectList = {
          'imglist' : [],
          'linkTypes' : [
              {'name':'PHYSICAL','id':'Physical'},
              {'name':'PORT_CHANNEL', 'id':'Port-Channel'},
              {'name':'VPC_MEMBER', 'id':'VPC-Member'},
              {'name':'VPC_PEER','id':'VPC-Peer'}
            ]
        };
        var tierData = {
          'Core' : { 'tier': 'Core', 'tier_display': 'Core Router', 'model': '', 'image_profile': '' },
          'Border' : { 'tier': 'Border', 'tier_display': 'Border Router', 'model': '', 'image_profile': '' }
        };

        $scope.submitData = {
            'name': '',
            'model_name': 'Leaf-Spine',
            'defaults': {
                'switches': [
                    { 'tier': 'Spine', 'tier_display': 'Spine', 'model': '', 'image_profile': '' },
                    { 'tier': 'Leaf', 'tier_display': 'Leaf', 'model': '', 'image_profile': '' }
                ],
                'links': [
                    {
                        'src_tier': 'Spine',
                        'dst_tier': 'Leaf',
                        'link_type': '',
                        'num_links': 1
                    }
                ]
            }
        };

        $scope.addTier = function(tier) {
          $scope.submitData.defaults.switches.push(tierData[tier]);
          $scope.show[tier] = true;
        }

        $scope.isObjectEmpty = function(object) {
          if(object === undefined || object === null || object === '' || object.length === 0){
              return true;
          }
          return false;
        };

        $scope.fetchTierSwitches = function(tier) {
          var reqHeader = {
                appendToURL : true,
                value : "?tier="+tier,
                noTrailingSlash : true
            };
         
          appServices.doAPIRequest(appSettings.appAPI.switches.list, null, reqHeader).then(function(data) {
            $scope.selectList[tier] = data;
            /*if(!$scope.isObjectEmpty($scope.selectList[tier]) && !$scope.isObjectEmpty($scope.submitData.defaults.switches)){
              $scope.submitData.defaults.switches = $scope.submitData.defaults.switches.filter(function(a) {
                if(a.tier == tier) {
                  a.model = $scope.selectList[tier][0].id;
                }
                return a;
              });
            }*/
          });
        };

        $scope.init = function() {
          this.fetchTierSwitches('Core');
          this.fetchTierSwitches('Spine');
          this.fetchTierSwitches('Leaf');
          this.fetchTierSwitches('Border');
          var reqHeader = {
                appendToURL : true,
                value : '?state=true',
                noTrailingSlash : true
            };

          appServices.doAPIRequest(appSettings.appAPI.images.list, null, reqHeader).then(function(data) {
            $scope.selectList.imglist = data;
          });
          if(!$scope.isObjectEmpty($scope.selectList.linkTypes) && !$scope.isObjectEmpty($scope.submitData.defaults.links)){
              for(var i=0; i<$scope.submitData.defaults.links.length; i++){
                $scope.submitData.defaults.links[i].link_type = $scope.selectList.linkTypes[0].id;
              }
          }
        };

        $scope.ok = function() {
          $modalInstance.close({
                submitData : $scope.submitData,
                action : $scope.action
            });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.init();
  });
