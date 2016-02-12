'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('GroupsCtrl', function($scope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
    /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
    appServices.setInternalAppUI($scope)
    var parent = $scope.$parent;
    $scope.groups = [];

    $scope.deleteGroup = function(id) {
        $scope.selectedId = id;
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

    $scope.createGrp = function() {
      $scope.action = "add";
      $scope.selectedId = null;
      $scope.openCreateModal();
    };

    $scope.openCreateModal = function() {
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

    $scope.submitData = function(modalData) {
    	//$location.path('/group/edit/1');
        if(modalData.action == 'add') {
            var dataToSubmit = modalData.submitData;
            appServices.doAPIRequest(appSettings.appAPI.group.create, dataToSubmit, null).then(function(data) {
                $location.path('/group/edit/'+data.id);
            });
        } else if(modalData.action == 'delete') {
            var requestHeader = {
                appendToURL: true,
                value: $scope.selectedId,
                noTrailingSlash: true
            };

            appServices.doAPIRequest(appSettings.appAPI.group.delete, null, requestHeader).then(function(data) {
                $scope.init();
            });
        }
    };

    $scope.transformData = function() {
        debugger;
        $scope.groups.filter(function(group){
            var switchlist = '';
            group.switch_list.filter(function(grpSwitch){
                switchlist = switchlist+grpSwitch.switch_name+', ';
            });
            switchlist = switchlist.substring(0,switchlist.length-2);
            if (switchlist.length > 50) {
              switchlist = switchlist.substring(0, 55) + '...';
              console.log('--------NEW Switch Name----------');
              console.log(switchlist);
            }
            group.switchlist = switchlist;
            return group;
        });
    };

    $scope.getGroupsList = function() {
        appServices.doAPIRequest(appSettings.appAPI.group.list, null, null).then(function(data) {
            $scope.groups = data;
            $scope.transformData();
            $scope.tableParams.reload();
        });
    };
    
    $scope.init = function(mode) {
        $scope.getGroupsList();
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
            appServices.tablePagination($defer, $filter, params, $scope.groups, $scope.searchKeyword);
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

angular.module('PoapServer').controller('GroupCreateCtrl',
      function($scope, $modalInstance, appSettings, appServices, dataToModal){
        $scope.action = dataToModal.action;

      	$scope.ok = function() {
          $modalInstance.close({
                submitData : $scope.submitData,
                action : $scope.action
            });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.init = function () {
            if('edit' == $scope.action) {
                $scope.submitData = angular.copy(dataToModal.submitData);
            }
        };

        $scope.init();
});