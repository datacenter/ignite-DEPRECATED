'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('ConfigurationCtrl', function($scope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
        /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope)
        var parent = $scope.$parent;
        $scope.configurations = [];

	    $scope.tableParams = new ngTableParams({
	            page: 1,
	            count: appSettings.tableSettings.count,
	            sorting: {
	                "name": "asc"
	            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.configurations, $scope.searchKeyword);
            }
        });

        $scope.getConfigurationList = function() {
            appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, null).then(function(data) {
                $scope.configurations = data;
                $scope.tableParams.reload();
            });
        };

        $scope.deleteConfiguration = function(profileindex_id, id, $index) {

                $scope.selectedId = profileindex_id;
                $scope.latest_version_id = id;

                var modalInstance = $modal.open({
                    animation: $scope.animationsEnabled,
                    templateUrl: 'pages/template/modal/configletDelete.html',
                    controller: 'ConfigDeleteCtrl',
                    size: 'md',
                    backdrop: 'static',
                    resolve: {
                        dataToModal : function() {
                            return {
                                id : $scope.selectedId,
                                action : 'delete',
                                callerScope : $scope
                            }
                        }
                     }
                });

                modalInstance.result.then(function(modalData) {
                    $scope.delete_type = modalData.submitData.delete_operation;
                    $scope.deleteConfirm();

                }, function() {
                    $log.info('Modal dismissed at: ' + new Date());
                });
        };

        $scope.deleteConfirm = function() {
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
                            action : 'delete',
                            message : 'Are you sure you want to delete?',
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


        $scope.submitData = function(modalData) {
            if(modalData.action == 'delete') {

                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                if($scope.delete_type === 'delete_latest') {
                    reqHeader.value = reqHeader.value+'/profile/'+$scope.latest_version_id;
                }

                appServices.doAPIRequest(appSettings.appAPI.configuration.delete, null, reqHeader).then(function(data) {
                    /* TODO after delete success */
                    // $scope.tableParams.reload();
                    $scope.init();
                });
            }
        };


       $scope.init = function() {
            $scope.getConfigurationList();
       };

       $scope.init();

       $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
       });
});