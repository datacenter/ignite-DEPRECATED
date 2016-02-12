'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('JobsCtrl', function($scope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
    /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
    appServices.setInternalAppUI($scope)
    var parent = $scope.$parent;
    $scope.jobs = [];

    $scope.getJobsList = function() {
        appServices.doAPIRequest(appSettings.appAPI.job.list, null, null).then(function(data) {
            $scope.jobs = data;
            $scope.tableParams.reload();
        });
    };

    $scope.deleteJob = function(id) {
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
                        message: 'Are you sure you want to delete this job?',
                        callerScope: $scope
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
                $scope.doDeleteJob(modalData);

        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.doDeleteJob = function() {
        var reqHeader = {
            appendToURL : true,
            value : $scope.selectedId,
            noTrailingSlash : true
        };
        appServices.doAPIRequest(appSettings.appAPI.job.delete, null, reqHeader).then(function(data) {
            $scope.init();
        });
    };

    $scope.init = function(mode) {
        $scope.getJobsList();
    };

    /**For table pagination**/
    $scope.tableParams = new ngTableParams({
        page: 1,
        count: appSettings.tableSettings.count,
        sorting: {
            "name": "asc"
        }
    }, {
        counts:[],
        getData: function($defer, params) {
            appServices.tablePagination($defer, $filter, params, $scope.jobs, $scope.searchKeyword);
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