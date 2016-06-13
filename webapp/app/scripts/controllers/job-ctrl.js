'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('Job_Ctrl', function($scope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, $routeParams) {
    /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
    appServices.setInternalAppUI($scope)
    var parent = $scope.$parent;
    $scope.selectList = {
        currentDate : new Date(),
        groups : [],
        images : []
    };

    $scope.job = {
      "name": "",
      "schedule": "",
      "tasks": []
    };

    /*$scope.viewImage = function(data) {
        $scope.action = "view";
        $scope.openImageModal(data);
    };*/

    $scope.viewImage = function(data,imgId) {
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/imagesModal.html',
            controller: 'ImagesModalCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        action : "view",
                        callerScope : $scope,
                        id : imgId,
                        image : data,
                        source : 'jobs'
                    }
                }
             }
        });
        $scope.modalInstance.result.then(function(modalData) {
            console.log('do nothing');
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.viewGroup = function(group_detail, grpId) {
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/jobGrpStatus.html',
            controller: 'JobGrpStatusCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        action : $scope.action,
                        callerScope : $scope,
                        groupName : group_detail.group_name,
                        /*id : $scope.imageId,*/
                        grpId : grpId,
                        new_item : group_detail.new_item,
                        grpStatus : group_detail.switches
                    }
                }
             }
        });
        $scope.modalInstance.result.then(function(modalData) {
            console.log('do nothing');
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    }

    $scope.prepareSchedule = function(){
        try{
            $scope.job.scheduleDate.setHours($scope.job.scheduleTime.getHours());
            $scope.job.scheduleDate.setMinutes($scope.job.scheduleTime.getMinutes());
            $scope.job.scheduleDate.setSeconds(0);
        } catch(e) {
            var date = new Date();
            $scope.job.scheduleDate.setHours(date.getHours());
            $scope.job.scheduleDate.setMinutes(date.getMinutes());
            $scope.job.scheduleDate.setSeconds(0);
        }
        
    };
    
    $scope.goBack = function(path) {
        $location.path(path);
    };

    $scope.getGroupStatus = function() {
        $scope.job.tasks = $scope.job.tasks.filter(function(a) {
            /*if(a.status == undefined && 'SCHEDULED' == $scope.job.status) {
                a.status = {
                    status : $scope.job.status
                };
            } else if(a.status == undefined){
                a.status = {
                    status : '--'
                };
            }*/
            if(a.type != undefined) {
                a.type_display = appSettings.fieldValues.jobs.upgrade_type.filter(function(b){
                    if(b.value == a.type) {
                        return b;
                    }
                })[0].label;
            }
            if('' == a.status || null == a.status) {
                a.status = '--';
            }
            return a;
        });
    };

    $scope.init = function() {
        $scope.mode = $routeParams.mode;
        $scope.selectedId = $routeParams.id;

        $scope.hstep = 1;
        $scope.mstep = 1;

        $scope.job.scheduleDate = $scope.selectList.currentDate;

        if('add' != $scope.mode) {
            var reqHeader = {
                appendToURL : true,
                value : $scope.selectedId,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.job.getById, null, reqHeader).then(function(data) {
                $scope.job = data;
                $scope.job.scheduleTime = new Date(data.schedule);
                $scope.job.scheduleDate = new Date(data.schedule);
                $scope.getGroupStatus();
                /*if($scope.job.status != 'SCHEDULED') {
                    $scope.hstep = 0;
                    $scope.mstep = 0;
                }*/
            });
            /*if('view' == $scope.mode) {
                $scope.hstep = 0;
                $scope.mstep = 0;
            }*/
        }

        this.fetchRequiredList();
    };

    $scope.save = function() {
        $scope.doSubmit();
    };

    $scope.doSubmit = function() {
        $scope.job.schedule = angular.copy($scope.job.scheduleDate);
        $scope.job.schedule = $scope.job.schedule.toISOString();
        if($scope.mode == 'add') {
            appServices.doAPIRequest(appSettings.appAPI.job.add, $scope.job, null).then(function(data) {
                $scope.goBack('/jobs');
            });
        } else if($scope.mode == 'edit') {
            var reqHeader = {
                appendToURL : true,
                value : $scope.selectedId,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.job.edit, $scope.job, reqHeader).then(function(data) {
                $scope.goBack('/jobs');
            });
        }
    };

    $scope.deleteJob = function() {
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
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
            $scope.goBack('/jobs');
        });
    };

    $scope.fetchRequiredList = function() {
        appServices.doAPIRequest(appSettings.appAPI.job.getGroupList, null, null).then(function(data) {
            $scope.selectList.groups = data;
        });
        appServices.doAPIRequest(appSettings.appAPI.images.list, null, null).then(function(data) {
            $scope.selectList.images = data;
        });
    };


  var checkPosition = function(positionHelper) {
            if(positionHelper == 'start') {
                return 0
            }

            else if(positionHelper == 'end') {
                return $scope.job.tasks.length;
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

  $scope.groupDialog = function(action, positionHelper, index){
        var position = checkPosition(positionHelper);
            if(position === false) {
                return;
            }

            var jobTask = {};

            if(index !== undefined) {
                jobTask = $scope.job.tasks[index];
            }

            $scope.taskModalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/addGrpTaskModal.html',
                controller: 'AddTaskToJobCtrl',
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
                            groups : $scope.selectList.groups,
                            images : $scope.selectList.images,
                            job : jobTask
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

    $scope.addEditTask = function(modalData) {
        if('add' == modalData.action) {
            $scope.job.tasks.splice(modalData.position, 0, modalData.submitData);
        }
        if('edit' == modalData.action) {
            $scope.job.tasks.splice(modalData.index, 1, modalData.submitData);
        }
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
                        message: 'Are you sure you want to delete this task from the current job?',
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
        $scope.job.tasks.splice(modalData.index, 1);
        if(typeof $scope.taskModalInstance != 'undefined') {
            $scope.taskModalInstance.dismiss();
        }
    };
  

    /** Datepicker **/
  $scope.open = function($event) {
    $scope.status.opened = true;
  };

  $scope.dateOptions = {
    formatYear: 'yy',
    startingDay: 1
  };

  

  $scope.status = {
    opened: false
  };
  //Added for timepicker
 //$scope.mytime = new Date();
    /*$scope.$watch("minutes", function () {
        if('view' == $scope.mode) {
            $('.ScheduleTimePicker button').prop('disabled',true);
        } else if('edit' == $scope.mode && $scope.job.status != 'SCHEDULED') {
            $('.ScheduleTimePicker button').prop('disabled',true);
        }
    });*/

    $scope.ismeridian = false;
    $scope.init();
});

angular.module('PoapServer').controller('AddTaskToJobCtrl', function($scope, $modalInstance, $modal, appServices, appSettings, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.mode = dataToModal.mode;
    $scope.defaultEdit = true;
    $scope.showDefault = false;
    $scope.selectList = {
        images : angular.copy(dataToModal.images),
        groups : angular.copy(dataToModal.groups),
        scripts : []
    }
    $scope.paramStructure = {
                "param_name": "",
                "param_type": "",
                "param_val": ""
            };
    $scope.task = {
        "group_id": "",
        "image_id": "",
        "run_size": 1,
        "retry_count": 0,
        "type": "",
        "type_display": "--",
        "status": "--",
        "failure_action_ind":appSettings.defaultData.jobs.failure_action,
        "failure_action_grp":appSettings.defaultData.jobs.failure_action,
        "group" : {
            "group_name" : "",
            "new_item": true
        }
    };

    $scope.init = function() {
        if($scope.action == 'view' || $scope.action == 'edit') {
            $scope.task = angular.copy(dataToModal.job);
            appServices.doAPIRequest(appSettings.appAPI.job.getScripts, null, null).then(function(data) {
                $scope.selectList.scripts = data;
            });
        }
        if($scope.action == 'view') {
            $scope.defaultEdit = false;
        }
    };

    $scope.changeAction = function(action) {
        $scope.action = action;
        if(action == 'edit') {
            $scope.defaultEdit = true;
        }
    };

    $scope.taskTypeChange = function() {
        if($scope.task.type == 'custom') {
            $scope.task.params = [];
            if($scope.selectList.scripts.length == 0) {
                appServices.doAPIRequest(appSettings.appAPI.job.getScripts, null, null).then(function(data) {
                    $scope.selectList.scripts = data;
                });
            }
        } else {
            delete $scope.task.params;
        }
    };

    $scope.addParam = function() {
        $scope.task.params.push(angular.copy($scope.paramStructure));
    };

    $scope.deleteParam = function(index) {
        $scope.task.params.splice(index,1);
    };

    $scope.transformData = function() {
        $scope.selectList.images.filter(function(a){
            if(a.id == $scope.task.image_id) {
                $scope.task.image_name = a.profile_name;
            }
        });
        $scope.selectList.groups.filter(function(a){
            if(a.id == $scope.task.group_id) {
                $scope.task.group.group_name = a.name;
            }
        });
        $scope.appSettings.fieldValues.jobs.upgrade_type.filter(function(a){
            if(a.value == $scope.task.type) {
                $scope.task.type_display = a.label;
            }
        });
    };

    $scope.toggleDefaultShow = function() {
        $scope.showDefault = !$scope.showDefault;
    };

    $scope.ok = function() {
        this.transformData();
        $modalInstance.close({
            submitData : $scope.task,
            action : $scope.action,
            position : dataToModal.position,
            index : dataToModal.index
        });
    };

    $scope.deleteTask = function() {
        dataToModal.callerScope.deleteTask(dataToModal.id, dataToModal.index);
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.init();

});
angular.module('PoapServer').controller('JobGrpStatusCtrl', function($scope, $modalInstance, $modal, appServices, appSettings, dataToModal) {
    $scope.grpSwitches = dataToModal.grpStatus;
    $scope.groupName = dataToModal.groupName;
    $scope.appSettings = appSettings;
    /*$scope.grpStatus = dataToModal.grpStatus.status;
    $scope.grp_switch_status=dataToModal.grpStatus.switches;
    $scope.statusEmptyFlag = false;
    if($scope.grp_switch_status == undefined || $scope.grp_switch_status.length < 1) {
        $scope.statusEmptyFlag = true;
    }*/

    $scope.mapDetails = function() {
        if($scope.statusEmptyFlag && ($scope.grpStatus == 'SCHEDULED' || $scope.grpStatus == '--')) {
            $scope.grpSwitches = $scope.grpSwitches.filter(function(a){
                a.status = $scope.grpStatus;
                return a;
            }); 
        } else if($scope.grpStatus == 'SCHEDULED' || $scope.grpStatus == '--') {
            $scope.grpSwitches = $scope.grpSwitches.filter(function(grpSwitches){
                var foundFlag = false;
                $scope.grp_switch_status.filter(function(grpStatus){
                    if(grpSwitches.switch_id == grpStatus.id){
                        foundFlag = true;
                        grpSwitches.status = grpStatus.status;
                        grpSwitches.log = grpStatus.log;
                        grpSwitches.ctime = grpStatus.ctime;
                    }
                });
                if(!foundFlag) {
                    grpSwitches.status = $scope.grpStatus;
                }
                return grpSwitches;
            });
        } else {
            $scope.grpSwitches = $scope.grp_switch_status;
        }
    };

    $scope.openLog = function(logMsg) {
      var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        action: 'log',
                        message: logMsg,
                        callerScope: $scope
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
                console.log('do nothing');

        }, function() {
            console.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.init = function() {
        if(dataToModal.new_item) {
            var requestHeader = {
                appendToURL: true,
                value: dataToModal.grpId,
                noTrailingSlash: true
            };
            appServices.doAPIRequest(appSettings.appAPI.group.getById, null, requestHeader).then(function(data) {
                $scope.grpSwitches = data.switch_list;
                $scope.grpSwitches.filter(function(swtch){
                    if('' == swtch.status || null == swtch.status) {
                        swtch.status = '--'
                    }
                    if('' == swtch.ctime || null == swtch.ctime) {
                        swtch.ctime = '--'
                    }
                });
                /*$scope.groupName = data.name;
                $scope.mapDetails();*/
            });
        } else {
            $scope.grpSwitches.filter(function(swtch){
                if('' == swtch.status || null == swtch.status) {
                    swtch.status = '--'
                }
                if('' == swtch.ctime || null == swtch.ctime) {
                    swtch.ctime = '--'
                }
            });
        }

        
        /**/
        
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.init();
});