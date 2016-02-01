'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
.controller('DeployedFabricCtrl', function($scope, $location,$filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
      /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope)

        var parent = $scope.$parent;
        $scope.deployedFabrics = [];

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.deployedFabrics, $scope.searchKeyword);

            }
        });

        $scope.selectedId = null;

        $scope.getDeployedFabrics = function() {
             appServices.doAPIRequest(appSettings.appAPI.deployedFabrics.list, null, null).then(function(data) {
                //callback.call(this, data)
                $scope.deployedFabrics = data;
                $scope.tableParams.reload();
            });

        }

        $scope.init = function(mode) {
            $scope.getDeployedFabrics()
        };



        
        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });

        $scope.init();

        //$scope.init();
});

//FabricReplicaCtrl


angular.module('PoapServer')
.controller('FabricReplicaCtrl', function($scope, $location, $routeParams, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
      /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        $scope.appSettings = appSettings;
        appServices.setInternalAppUI($scope)
        var parent = $scope.$parent;
        $scope.fabricID = $routeParams.fabricID;
        $scope.replicaNumber = $routeParams.replicaNumber;
        $scope.replicaDetailsStats = [];

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "switch_name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.replicaDetailsStats, $scope.searchKeyword);

            }
        });

        $scope.openConfigModal = function(statId) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/fabricConfigView.html',
                controller: 'ViewFabricConfigModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            "statId" : statId
                        }
                    }
                 }
            });
            $scope.modalInstance.result.then(function(modalData) {
               $log.info('Modal dismissed at: ' + new Date());
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };


        $scope.openLogModal = function(statId) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/logs.html',
                controller: 'ViewFabricLogModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            "statId" : statId
                        }
                    }
                 }
            });
            $scope.modalInstance.result.then(function(modalData) {
                $log.info('Modal dismissed at: ' + new Date());
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        
       $scope.openRuleModal = function(id) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/ruleModal.html',
                controller: 'RuleModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : "external",
                            id : id,
                            configurations : $scope.configurations,
                            callerScope : $scope
                        }
                    }
                 }
            });

            $scope.modalInstance.result.then(function(modalData) {
                
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });

        };

        

        $scope.getReplicaDetails = function() {

            var urlParam = $scope.fabricID + "/" + $scope.replicaNumber
            var reqHeader = {
                appendToURL : true,
                value : urlParam,
                noTrailingSlash : true
            };

            appServices.doAPIRequest(appSettings.appAPI.deployedFabrics.replicaDetails, null, reqHeader).then(function(data) {
                //callback.call(this, data)
                $scope.replicaDetails = data;
                $scope.replicaDetailsStats = data.stats;
                $scope.tableParams.reload();
            });
        };

        $scope.getConfigurationList = function() {
            appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, null).then(function(data) {
                $scope.configurations = data;
            });
        };
          
        $scope.init = function(mode) {
            $scope.getConfigurationList();
            $scope.getReplicaDetails();
        };

        $scope.init();
        
});


angular.module('PoapServer').controller('ViewFabricConfigModalCtrl', function($scope, $modalInstance, FileReader, appSettings, appServices, dataToModal) {
      
    $scope.getConfigDetails = function(statId) {
            var reqHeader = {
                appendToURL : true,
                value : statId,
                noTrailingSlash : true
            };

            appServices.doAPIRequest(appSettings.appAPI.deployedFabrics.getConfig, null, reqHeader).then(function(data) {
                $scope.configDetails = data;
            });
        };

    $scope.close = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.getConfigDetails(dataToModal.statId);
});



