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

    $scope.cloneJob = function(id,name) {
        $scope.action = "clone";
        $scope.selectedId = id;
        $scope.openCloneModal(name);
    };

    $scope.openCloneModal = function(name) {
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/cloneModal.html',
            controller: 'JobCloneCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        action : $scope.action,
                        id : $scope.selectedId,
                        job_name : name,
                        source : 'job'
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
        var reqHeader = {
            appendToURL : true,
            value : $scope.selectedId+"/clone",
            noTrailingSlash : true
        };
        if(modalData.action == 'clone') {
            appServices.doAPIRequest(appSettings.appAPI.job.clone, modalData.submitData, reqHeader).then(function(data) {
                $scope.getJobsList();
            });
        }
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

angular.module('PoapServer').controller('JobCloneCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {
    $scope.source = dataToModal.source;
    $scope.action = dataToModal.action;
    $scope.id = dataToModal.id;
    $scope.submitData = {
      "name" : dataToModal.job_name+"_clone",
      "schedule" : new Date()
    }

    $scope.job = {
        currentDate : new Date()
    }

    $scope.prepareSchedule = function(){
        try{
            $scope.submitData.schedule.setHours($scope.job.scheduleTime.getHours());
            $scope.submitData.schedule.setMinutes($scope.job.scheduleTime.getMinutes());
            $scope.submitData.schedule.setSeconds(0);
        } catch(e) {
            var date = new Date();
            $scope.job.scheduleDate.setHours(date.getHours());
            $scope.job.scheduleDate.setMinutes(date.getMinutes());
            $scope.job.scheduleDate.setSeconds(0);
        }
        
    };

    $scope.ok = function() {
        $scope.submitData.schedule = $scope.submitData.schedule.toISOString();
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            id : $scope.id
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.init = function() {};

    /** Datepicker **/
    $scope.open = function($event) {
        $scope.status.opened = true;
    };

    $scope.dateOptions = {
        formatYear: 'yy',
        startingDay: 1
    };

    $scope.hstep = 1;
    $scope.mstep = 1;

    $scope.status = {
        opened: false
    };

    $scope.ismeridian = false;

    $scope.init();
  });