'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('TaskCtrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {

    appServices.setInternalAppUI($scope);

    var parent = $scope.$parent;
    $scope.tasks = [];
    $scope.selectedId = null;

    $scope.addTask = function() {
        $scope.action = 'add';
        $scope.selectedId = null;
        this.openTaskModal();
    };

    $scope.viewTask = function(id, index) {
        console.info(id);
        $scope.action = "view";
        $scope.selectedId = id;
        $scope.openTaskModal(index);
    };

    $scope.editTask = function(id, index) {
        $scope.action = "edit";
        $scope.selectedId = id;
        $scope.openTaskModal(index);
    };

    $scope.deleteTask = function(id, index) {
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
                        message: 'Are you sure you want to delete the task?',
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
    };

    $scope.openTaskModal = function(index) {
        $scope.taskModalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/taskModal.html',
            controller: 'TaskModalCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    var dtm = {
                        action : $scope.action,
                        index : index,
                        callerScope : $scope,
                        page : 'task',
                        id : $scope.selectedId
                    };

                    return dtm;
                }
             }
        });

        $scope.taskModalInstance.result.then(function(data) {
            $scope.submitData(data);
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.submitData = function(modalData) {
        /* this is for add */
            if(modalData.action == 'add') {
                var dataToSubmit = modalData.submitData;
                var reqHeader = {};
                appServices.doAPIRequest(appSettings.appAPI.task.add, dataToSubmit, null).then(function(data) {
                   $scope.init('add');
                });
            }

            else if(modalData.action == 'edit') {

                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                var dataToSubmit = modalData.submitData;

                appServices.doAPIRequest(appSettings.appAPI.task.edit, dataToSubmit, reqHeader).then(function(data) {
                    /* TODO after delete success */
                    $scope.init('edit');
                    if(typeof $scope.modalInstance != 'undefined') {
                        $scope.modalInstance.dismiss();
                    }
                });
            }

            else if(modalData.action == 'delete') {

                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                appServices.doAPIRequest(appSettings.appAPI.task.delete, null, reqHeader).then(function(data) {
                    /* TODO after delete success */
                    $scope.init('delete');
                    if(typeof $scope.taskModalInstance != 'undefined') {
                        $scope.taskModalInstance.dismiss();
                    }
                });
            }

    };

    $scope.init = function(mode) {
        $scope.getTaskList();
    };

    $scope.getTaskList = function() {
        appServices.doAPIRequest(appSettings.appAPI.task.list, null, null).then(function(data) {
            console.log('*******************************************'+JSON.stringify(data)+'****************************************');
            $scope.tasks = data;
            $scope.tableParams.reload();
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
            appServices.tablePagination($defer, $filter, params, $scope.tasks, $scope.searchKeyword);
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

angular.module('PoapServer').controller('TaskModalCtrl', function($scope, $modalInstance, appServices, appSettings, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.paramSize = 0;

    $scope.methodList = ["sftp", "tftp", "http", "scp"];

    $scope.submitData = {
    "page" : dataToModal.page,
    "task" :
      {
            "name":"",
            "desc":"",
            "function":"",
            "handler":"",
            "parameters":{
                "":""
                },
        
            "location_server_ip": "",
            "location_server_user": "",
            "location_server_password": "",
            "location_access_protocol": "",
      }
    };

    $scope.addParam = function() {
        $scope.submitData.task.parameters[""]="";
        $scope.paramSize = Object.keys($scope.submitData.task.parameters).length;
    };

    $scope.editParam = function(key) {
        $scope.submitData.task.parameters[key]="";
        $scope.paramSize = Object.keys($scope.submitData.task.parameters).length;
        if($scope.paramSize > 1) {
            delete $scope.submitData.task.parameters[""];
            $scope.paramSize = Object.keys($scope.submitData.task.parameters).length;
        }
    };

    $scope.removeParam = function(key) {
        delete $scope.submitData.task.parameters[key];
        $scope.paramSize = Object.keys($scope.submitData.task.parameters).length;
    };

    $scope.$watch("submitData.task.parameters", function() {
        debugger;
      $scope.paramSize = Object.keys($scope.submitData.task.parameters).length;
    });

    $scope.ok = function() {
        debugger;
        delete $scope.submitData.task.parameters[""];
        console.log($scope.submitData);
        $modalInstance.close({
            submitData : $scope.submitData.task,
            action : $scope.action,
            index : dataToModal.index
        });
    };
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.deleteTask = function() {
        dataToModal.callerScope.deleteTask(dataToModal.id, dataToModal.index);
    };

    $scope.changeAction = function(newAction) {
        if(newAction == "edit" && JSON.stringify($scope.submitData.task.parameters).length < 3) {
            $scope.submitData.task.parameters = {"":""};
        }
        $scope.action = newAction;
    };

    $scope.getData = function() {
        if($scope.action ==  'view' || $scope.action == 'edit') {
            var reqHeader = {
                appendToURL : true,
                value : dataToModal.id,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.task.getById, null, reqHeader).then(function(data) {
                $scope.submitData.task = data;
            });
        }
    };

    $scope.init = function(){
        $scope.getData();
    };

    $scope.init();

});
