'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('WorkflowCtrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {

  	appServices.setInternalAppUI($scope);

    var parent = $scope.$parent;
    $scope.workflows = [];
    $scope.selectedId = null;

    $scope.init = function() {
    	this.getWorkflowLists();
    };

    $scope.getWorkflowLists = function() {
    	appServices.doAPIRequest(appSettings.appAPI.workflow.list, null, null).then(function(data) {
            console.info('*******************************************'+data+'****************************************');
            $scope.workflows = data;
            $scope.tableParams.reload();
        });
    };

    $scope.deleteWorkflow = function(id, $index) {
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
                        message: 'Are you sure you want to delete the workflow?',
                        callerScope: $scope
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
            $scope.doDeleteWorkflow(modalData);
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.doDeleteWorkflow = function(modalData) {
        var reqHeader = {
            appendToURL : true,
            value : $scope.selectedId,
            noTrailingSlash : true
        };

        appServices.doAPIRequest(appSettings.appAPI.workflow.delete, null, reqHeader).then(function(data) {
            /* TODO after delete success */
            // $scope.tableParams.reload();
            $scope.init();
        });
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
            appServices.tablePagination($defer, $filter, params, $scope.workflows, $scope.searchKeyword);
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

angular.module('PoapServer').controller('WorkflowDeleteModalCtrl',
    function($scope, $modalInstance, FileReader, appSettings, appServices, dataToModal) {
        $scope.ok = function() {
            $modalInstance.close({
                action : 'delete',
                id : dataToModal.id,
                index : dataToModal.index
            });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };
});