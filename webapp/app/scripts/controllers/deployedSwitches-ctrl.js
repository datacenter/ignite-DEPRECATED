'use strict';

angular.module('PoapServer')
.controller('DeployedSwitchesCtrl', function($scope, $location, $routeParams, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
      /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        $scope.appSettings = appSettings;
        appServices.setInternalAppUI($scope)
        var parent = $scope.$parent;
        $scope.switchDetailsStats = [];

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "switch_name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.switchDetailsStats, $scope.searchKeyword);

            }
        });

        $scope.openConfigModal = function(statId) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/fabricConfigView.html',
                controller: 'DeployedSwitchConfigModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            "statId" : statId,
                            "type" : "depConfig"
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
                            imglist : $scope.imglist,
                            workflow_list : $scope.workflow_list,
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

        

        $scope.getSwitchDetails = function() {
            
            $scope.tableParams.reload();
            appServices.doAPIRequest(appSettings.appAPI.deployedSwitches.list, null, false).then(function(data) {
                $scope.switchDetailsStats = data;
                angular.forEach($scope.discoveryRules, function(value,key){
                    $scope.switchDetailsStats = $scope.switchDetailsStats.filter(function(a){
                        if(a.boot_detail.discovery_rule_name == undefined && a.boot_detail.discovery_rule == value.id) {
                            a.boot_detail.discovery_rule_name = value.name;
                        }
                        return a;
                    });
                })

                $scope.switchDetailsStats = $scope.switchDetailsStats.filter(function(a){
                        if(a.boot_detail.discovery_rule_name == undefined) {
                            a.boot_detail.discovery_rule_name = "--";
                        }
                        return a;
                    });
                $scope.tableParams.reload();
            });
        };

        /*$scope.getConfigurationList = function() {
            
        };

        $scope.getDiscoveryRules = function() {
            
        };*/

        $scope.fetchReqLists = function() {
            var reqHeader = {
                appendToURL: true,
                value: '?submit=true',
                noTrailingSlash: true
              };
            appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, null).then(function(data) {
                $scope.configurations = data;
            });
            appServices.doAPIRequest(appSettings.appAPI.discoveryRule.list, null, null).then(function(data) {
                $scope.discoveryRules = data;
                $scope.getSwitchDetails();
            });
            appServices.doAPIRequest(appSettings.appAPI.images.list, null, null).then(function(data) {
              $scope.imglist = data;
            });
            appServices.doAPIRequest(appSettings.appAPI.workflow.list, null, reqHeader).then(function(data) {
              $scope.workflow_list = data;
            });
        };
          
        $scope.init = function(mode) {
            $scope.fetchReqLists();
            /*$scope.getConfigurationList();
            $scope.getDiscoveryRules();*/
        };

        $scope.init();
        
});

angular.module('PoapServer').controller('DeployedSwitchConfigModalCtrl', function($scope, $rootScope, $modalInstance, FileReader, appSettings, appServices, dataToModal) {
      
    $scope.getConfigDetails = function(statId,type) {
            var reqHeader = {
                appendToURL : true,
                value : '',
                noTrailingSlash : true
            };

            if( 'depConfig' === type ) {
                reqHeader.value = statId;
                appServices.doAPIRequest(appSettings.appAPI.deployedSwitches.view_config, null, reqHeader).then(function(data) {
                    $scope.configDetails = data;
                });
            } else if ( 'pullConfig' === type ) {
                reqHeader.value = dataToModal.fabricId+'/switch/'+statId+'/config/latest';
                appServices.doAPIRequest(appSettings.appAPI.fabricInstance.switchConfig, null, reqHeader).then(function(data) {
                    $scope.configDetails = data;
                });
            }
        };

    $scope.close = function() {
        $modalInstance.dismiss('cancel');
    };

    /* watch for the error flag */

    $scope.$watch(function() {
        return $rootScope.errorFlag;
    },function() {
        if($rootScope.errorFlag == true)
            $scope.close();
    });

    $scope.getConfigDetails(dataToModal.statId,dataToModal.type);
});

angular.module('PoapServer').controller('ViewFabricLogModalCtrl', function($scope, $rootScope, $modalInstance, FileReader, appSettings, appServices, dataToModal) {
   
    $scope.close = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.getLogDetails = function(id) {
        var reqHeader = {
            appendToURL : true,
            value : id,
            noTrailingSlash : true
        };

        appServices.doAPIRequest(appSettings.appAPI.deployedSwitches.view_log, null, reqHeader).then(function(data) {
            $scope.logDetails = data;
        });
    };

    /* watch for the error flag */

    $scope.$watch(function() {
        return $rootScope.errorFlag;
    },function() {
        if($rootScope.errorFlag == true)
            $scope.close();
    });

    $scope.getLogDetails(dataToModal.statId);
});