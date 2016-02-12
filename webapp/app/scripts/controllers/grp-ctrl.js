'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('GrpCtrl', function($scope, $location,$routeParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService, $filter, ngTableParams) {
        /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope);
        var parent = $scope.$parent;
        $scope.checkbox = [];
        $scope.delSwitches = [];
        // $scope.delSwitchActive = false;
        $scope.delAllSwitches = false;
        $scope.grpSwitches = [];

        /**Configlets Modal**/

        $scope.animationsEnabled = true;

        $scope.goBack = function(path) {
            $location.path(path);
        };

        $scope.editGroupDetails = function() {
            $scope.modalInstance = $modal.open({
                    animation: $scope.animationsEnabled,
                    templateUrl: 'pages/template/modal/createGroupModal.html',
                    controller: 'GroupCreateCtrl',
                    size: 'md',
                    backdrop: 'static',
                    resolve: {
                        dataToModal : function() {
                            return {
                                action : $scope.action,
                                callerScope : $scope,
                                submitData : $scope.group
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

        $scope.deleteGroup = function() {
            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/deleteModal.html',
                controller: 'AlertModalCtrl',
                size: 'md',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            id : $scope.selectedId,
                            action: 'delete',
                            message: 'Are you sure you want to delete this group?',
                            callerScope : $scope
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

        $scope.selectAllSwitchesToggle = function() {
            $scope.delAllSwitches = !$scope.delAllSwitches;
            if($scope.delAllSwitches){
                $scope.grpSwitches.filter(function(a){
                    $scope.delSwitches.push({'switch_id':a.switch_id});
                });
            } else {
                $scope.grpSwitches.filter(function(a){
                    $scope.delSwitches.shift();
                });
            }
        };

        $scope.enableSwitchDelToggle = function() {
            // $scope.delSwitchActive = !$scope.delSwitchActive;
            $scope.delAllSwitches = false;
            /*if(!$scope.delSwitchActive && $('#selectAll').prop('checked')) {
                $("#selectAll").click();
            }*/
            $scope.grpSwitches.filter(function(a){
                $scope.delSwitches.shift();
            });
        };

        $scope.deleteSwitches = function() {
            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/deleteModal.html',
                controller: 'AlertModalCtrl',
                size: 'md',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            id : $scope.selectedId,
                            action: 'Delete Switches',
                            message: 'Are you sure you want to delete switche(s) from this group?',
                            callerScope : $scope
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

        $scope.addSwitch = function() {
        	$scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/switchList.html',
                controller: 'manageGrpSwitchCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : 'addSwitches',
                            switches : $scope.switches,
                            callerScope : $scope,
                            grpSwitches : $scope.grpSwitches
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

        $scope.getAllDeployedSwitches = function() {
        	appServices.doAPIRequest(appSettings.appAPI.deployedSwitches.list, null, null).then(function(data) {
                $scope.switches = data;
            });
        };

        $scope.submitData = function(modalData) {
            if(modalData.action == 'edit') {
                var requestHeader = {
                    appendToURL: true,
                    value: $scope.selectedId,
                    noTrailingSlash: true
                };

                appServices.doAPIRequest(appSettings.appAPI.group.edit, modalData.submitData, requestHeader).then(function(data) {
                    $scope.group = data;
                    $scope.groupData = angular.copy($scope.group);
                });
            } else if(modalData.action == 'addSwitches') {
                var requestHeader = {
                    appendToURL: true,
                    value: $scope.selectedId+'/switch',
                    noTrailingSlash: true
                };

                appServices.doAPIRequest(appSettings.appAPI.group.addSwitches, modalData.submitData, requestHeader).then(function(data) {
                    /*$scope.group = data;
                    $scope.groupData = angular.copy($scope.group);*/
                    $scope.grpSwitches = data.switch_list;
                    $scope.tableParams.reload();
                });
            } else if(modalData.action == 'delete') {
                var requestHeader = {
                    appendToURL: true,
                    value: $scope.selectedId,
                    noTrailingSlash: true
                };

                appServices.doAPIRequest(appSettings.appAPI.group.delete, null, requestHeader).then(function(data) {
                    $scope.goBack('/group');
                });
            } else if(modalData.action == 'Delete Switches') {
                var requestHeader = {
                    appendToURL: true,
                    value: $scope.selectedId+'/switch',
                    noTrailingSlash: true
                };

                appServices.doAPIRequest(appSettings.appAPI.group.delete, $scope.delSwitches, requestHeader).then(function(data) {
                    $scope.grpSwitches.filter(function(a){
                        $scope.delSwitches.shift();
                    });
                    $scope.group = data;
                    $scope.groupData = angular.copy($scope.group);
                    $scope.grpSwitches = $scope.group.switch_list;
                    $scope.tableParams.reload();
                    if($('#selectAll').prop('checked')) {
                        $("#selectAll").click();
                        $scope.delAllSwitches = !$scope.delAllSwitches;
                    }
                });
            }
        };

        $scope.processRequest = function() {
            var requestHeader = {
                appendToURL: true,
                value: $scope.selectedId,
                noTrailingSlash: true
            };
            appServices.doAPIRequest(appSettings.appAPI.group.getById, null, requestHeader).then(function(data) {
                $scope.group = data;
                $scope.groupData = angular.copy($scope.group);
                $scope.grpSwitches = $scope.group.switch_list;
                if($scope.grpSwitches.length == 0) {
                    $scope.grpSwitches = [];
                }
                $scope.tableParams.reload();
            });
        };

        $scope.init = function() {
        	$scope.action = $routeParams.mode;
        	$scope.selectedId = $routeParams.id;
            this.processRequest();
			$scope.getAllDeployedSwitches();			
        };

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.grpSwitches, $scope.searchKeyword);
            }
        });

        $scope.toggleAnimation = function() {
            $scope.animationsEnabled = !$scope.animationsEnabled;
        };

        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });

        $scope.init();
});


angular.module('PoapServer')
    .controller('manageGrpSwitchCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal, $filter, ngTableParams) {
    	$scope.appServices = appServices;
    	$scope.switches = angular.copy(dataToModal.switches);
    	$scope.selectedSwitches = [];
        $scope.action = dataToModal.action;

        $scope.ok = function() {
            $modalInstance.close({
                submitData : $scope.selectedSwitches,
                action : $scope.action
            });
        }

        $scope.tableParams = new ngTableParams({
	        page: 1,
	        count: appSettings.tableSettings.count,
	        sorting: {
	            "name": "asc"
	        }
	    }, {
	        counts:[],
	        getData: function($defer, params) {
	            appServices.tablePagination($defer, $filter, params, $scope.switches, $scope.searchKeyword);
	        }
	    });

	    $scope.toggleAnimation = function() {
	        $scope.animationsEnabled = !$scope.animationsEnabled;
	    };

	    $scope.$watch("searchKeyword", function () {
	        $scope.tableParams.reload();
	        $scope.tableParams.page(1);
	    });
    	$scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.init = function() {
            if('addSwitches' == $scope.action) {
                var index = 0;
                $scope.selectedSwitches = angular.copy(dataToModal.grpSwitches);
                console.log('selecetedSwitches : '+$scope.selectedSwitches);
                console.log('switches : '+$scope.switches);
                if($scope.selectedSwitches.length > 0 && $scope.switches.length > 0){
                    for(var i =0;i<$scope.selectedSwitches.length;i++) {
                        index = -1;
                        var foundIndex = -1;
                        $scope.switches.filter(function(a){
                            index++;
                            if(a.id == $scope.selectedSwitches[i].switch_id)
                            {
                                foundIndex = index;
                            }
                        });
                        if(foundIndex > -1) {
                            $scope.switches.splice(foundIndex,1);
                        }
                    }  
                }
                
            }
        };

        $scope.init();
});