'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('AddWorkflowCtrl', function($scope, $location,$routeParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {

    $scope.submitData = {
                    "name": "",
                    "submit"  : false,
                    "task_list"  : []
        };
    $scope.init = function(){
        $scope.mode = $routeParams.mode;
        $scope.workflowId = $routeParams.id;

        this.getTaskList();
        
    };

    $scope.getWorkflow = function() {
        var reqHeader = {
            appendToURL : true,
            value : $scope.workflowId,
            noTrailingSlash : true
        };
        appServices.doAPIRequest(appSettings.appAPI.workflow.getById, null, reqHeader).then(function(data) {
            $scope.submitData = data;
            angular.forEach($scope.submitData.task_list, function(value,key){
                $scope.task_list.filter(function(a){
                  if(a.id == value.task_id){
                    value.name = a.name;
                    // value.handler = a.handler;
                  }
                });
            });
            if($scope.mode == 'clone') {
                $scope.submitData.name="";
                $scope.submitData.submit=false;
            }
        });
    };

    $scope.deleteWorkflow = function(id) {
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
            $scope.doDeleteWorkflow($scope.selectedId);
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.doDeleteWorkflow = function(selectedId) {

        var reqHeader = {
            appendToURL : true,
            value : selectedId,
            noTrailingSlash : true
        };

        appServices.doAPIRequest(appSettings.appAPI.workflow.delete, null, reqHeader).then(function(data) {
            /* TODO after delete success */
            $location.path('/workflow');
        });
    };

    $scope.getTaskList = function(){
        appServices.doAPIRequest(appSettings.appAPI.task.list, null, null).then(function(data) {
            $scope.task_list = data;
            if($scope.mode == 'edit' ||  $scope.mode == 'view' ||  $scope.mode == 'clone') {
                $scope.getWorkflow();
            }
        });
    };

    $scope.deleteTask = function($index) {
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        index : $index,
                        action: 'delete',
                        message: 'Are you sure you want to delete this task from the workflow?',
                        callerScope: $scope
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
                $scope.doDeleteTask(modalData);

        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.doDeleteTask = function(modalData){
        $scope.submitData.task_list.splice(modalData.index, 1);
        if(typeof $scope.taskModalInstance != 'undefined') {
            $scope.taskModalInstance.dismiss();
        }
    };

    var checkPosition = function(positionHelper) {
            if(positionHelper == 'start') {
                return 0
            }

            else if(positionHelper == 'end') {
                return $scope.submitData.task_list.length;
            }

            else if(positionHelper == 'before' || positionHelper == 'after') {
                var $checkboxes = $('#taskList').find('.chk');
                var count = 0;
                var position = 0;
                $.each($checkboxes, function(key, val) {
                    if($(this).is(':checked') == true) {
                        count++;
                        position = key;
                    }
                })

                if(count == 0) {
                    alert('Select a row for this action.');
                    return false;
                }

                else if(count > 1) {
                    alert('More than one row cannot be selected for this action.');
                    return false;
                }


                if(positionHelper == 'before') {
                    return position;
                }

                else if(positionHelper == 'after') {
                    return position+1;
                }


            }

        };

    $scope.taskDialog = function(action, positionHelper, index){
        var position = checkPosition(positionHelper);
            if(position === false) {
                return;
            }

            var workflowTask = {};

            if(index !== undefined) {
                workflowTask = $scope.submitData.task_list[index];
            }

            $scope.taskModalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/taskModal.html',
                controller: 'AddTaskToWorkflowCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        var dtm = {
                            action : action,
                            position : position,
                            index : index,
                            mode : $scope.mode,
                            callerScope : $scope,
                            page : 'workflow',
                            task_list : $scope.task_list,
                            workflowTask : workflowTask
                        };

                        return dtm;
                    }
                 }
            });

            $scope.taskModalInstance.result.then(function(data) {
                $scope.addEditTask(data);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
    };

    $scope.addEditTask = function(data) {
        if(data.action == 'add') {
            $scope.submitData.task_list.splice(data.position, 0, data.submitData.task);
            //$scope.submitData.construct_list.push(data.submitData);
        }

        if(data.action == 'edit') {
            $scope.submitData.task_list.splice(data.index, 1, data.submitData.task);
        }
    };


    $scope.goBack = function(path) {
        $location.path(path);
    };

    $scope.save = function() {
        $scope.doSubmit();
    };

    $scope.submit = function() {
        $scope.submitData.submit = true;
        $scope.doSubmit();
    };

    $scope.doSubmit = function() {
        var mode = $routeParams.mode;
        if(mode == 'add' || mode == 'clone') {
            appServices.doAPIRequest(appSettings.appAPI.workflow.add, $scope.submitData, null).then(function(data) {
                $location.path('/workflow');
            });
        }
        else if(mode == 'edit') {
            var id = $routeParams.id;
            var reqHeader = {
                appendToURL : true,
                value : id,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.workflow.edit, $scope.submitData, reqHeader).then(function(data) {
                $location.path('/workflow');
            });
        }

    };

    $scope.init();

  });

angular.module('PoapServer').controller('AddTaskToWorkflowCtrl', function($scope, $modalInstance, $modal, appServices, appSettings, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.params_list = [];
    $scope.action = dataToModal.action;
    $scope.taskStructure = {
            "name":"",
            "desc":"",
            "function":"",
            "handler":"",
            "parameters":{},
            "location":{
                "method":"scp",
                "username":"user1",
                "password":"pwd",
                "hostname":"127.0.0.1"
            }
      };

    $scope.submitData = {
        "page" : dataToModal.page,
        "task_selected" : "",
        "task" : {}
    };

    $scope.task_list = [];

    $scope.configlets = [];

    /*$scope.resetValues = function() {
        $scope.submitData.configlet_id = '';
        $scope.params_list = [];
    };

    */

    $scope.editParamVal = function(key,value) {
        $scope.submitData.task.parameters[key]=value;
    };

    $scope.deleteTask = function() {
        dataToModal.callerScope.deleteTask(dataToModal.id, dataToModal.index);
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    };

    $scope.ok = function() {
        console.log($scope.submitData);
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            position : dataToModal.position,
            index : dataToModal.index
        });
    };
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.setValues = function() {
        if(undefined != dataToModal.workflowTask.id) {
            $scope.submitData.task_selected = dataToModal.workflowTask.id;
        } else if(undefined != dataToModal.workflowTask.task_id) {
            $scope.submitData.task_selected = dataToModal.workflowTask.task_id;
        }
        $scope.submitData.task = dataToModal.workflowTask;
    };

    $scope.getTaskDetails = function() {
        if('' !== $scope.submitData.task_selected) {
            var reqHeader = {
                appendToURL : true,
                value : $scope.submitData.task_selected,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.task.getById, null, reqHeader).then(function(data) {
                $scope.submitData.task = data;
                $scope.submitData.task.task_id = data.id;
            });
        }
    };

    $scope.init = function(){
        
        $scope.configletsCache = dataToModal.configlets;
        $scope.mode = dataToModal.mode;
        $scope.constructIndex = dataToModal.index;
        $scope.task_list = dataToModal.task_list;

        if(dataToModal.action == 'view' || dataToModal.action == 'edit') {
            $scope.setValues();
        }
    };

    /*$scope.deleteConstruct = function($index){
        dataToModal.callerScope.deleteConstruct($index);
    };*/

    $scope.init();

});
angular.module('PoapServer').controller('TaskDeleteModalCtrl',
    function($scope, $modalInstance, appSettings, appServices, dataToModal) {
        $scope.ok = function() {
            $modalInstance.close({
                action : 'delete',
                index : dataToModal.index
            });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };
});