'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('AAA_Ctrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {

    appServices.setInternalAppUI($scope);

    var parent = $scope.$parent;
    $scope.aaa_files = [];
    $scope.selectedId = null;

    $scope.addAAA_setup = function() {
        $scope.action = 'add';
        $scope.selectedId = null;
        this.openAAASetupModal();
    };

    $scope.view_aaa_setup = function(id,index) {
        $scope.action = 'view';
        $scope.selectedId = id;
        this.openAAASetupModal(index);
    };

    $scope.edit_aaa_setup = function(id,index) {
        $scope.action = 'edit';
        $scope.selectedId = id;
        this.openAAASetupModal(index);
    };

    $scope.deleteSetup = function(id, index) {
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
                        message: 'Are you sure you want to delete this setup?',
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


    $scope.openAAASetupModal = function(index) {
    	$scope.aaaModalInstance = $modal.open({
	        animation: $scope.animationsEnabled,
	        templateUrl: 'pages/template/modal/aaaSetupModal.html',
	        controller: 'AAA_SetupModalCtrl',
	        size: 'md',
	        backdrop: 'static',
	        resolve: {
	            dataToModal : function() {
	                var dtm = {
	                    action : $scope.action,
	                    index : index,
	                    callerScope : $scope,
	                    id : $scope.selectedId
	                };

	                return dtm;
	            }
	         }
	    });

	    $scope.aaaModalInstance.result.then(function(data) {
	        $scope.submitData(data);
	    }, function() {
	        $log.info('Modal dismissed at: ' + new Date());
	    });
    };

    $scope.submitData = function(modalData) {
        var reqHeader = {
            appendToURL : true,
            value : $scope.selectedId,
            noTrailingSlash : true
        };
        if(modalData.action == 'add') {
            appServices.doAPIRequest(appSettings.appAPI.aaa_server.add, modalData.submitData, null).then(function(data) {
               $scope.init();
            });
        } else if(modalData.action == 'delete') {
            appServices.doAPIRequest(appSettings.appAPI.aaa_server.delete, modalData.submitData, reqHeader).then(function(data) {
               $scope.init();
               if(typeof $scope.aaaModalInstance != 'undefined') {
                    $scope.aaaModalInstance.dismiss();
                }
            });
        } else if(modalData.action == 'edit') {
            appServices.doAPIRequest(appSettings.appAPI.aaa_server.edit, modalData.submitData, reqHeader).then(function(data) {
               $scope.init();
            });
        }
    };

    $scope.init = function() {
    	$scope.getAAAsetupList();
    };

    $scope.getAAAsetupList = function() {
        appServices.doAPIRequest(appSettings.appAPI.aaa_server.list, null, null).then(function(data) {
            $scope.aaa_files = data;
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
            appServices.tablePagination($defer, $filter, params, $scope.aaa_files, $scope.searchKeyword);
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
angular.module('PoapServer').controller('AAA_SetupModalCtrl',function($scope, $modalInstance, appServices, appSettings, dataToModal) {
	$scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.index = dataToModal.index;

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function() {
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            index : dataToModal.index
        });
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    };

    $scope.deleteSetup = function() {
        dataToModal.callerScope.deleteSetup(dataToModal.id, dataToModal.index);
    };

    $scope.serverProtocolCh = function() {
        if($scope.submitData.protocol == 'radius') {
            $scope.submitData.port = 1812;
        } else if($scope.submitData.protocol == 'tacacs+') {
            $scope.submitData.port = 49;
        } else {
            $scope.submitData.port = '';
        }
    };

    $scope.validateIPaddress = function()   
    {
        var ipPattern = /^([0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (!ipPattern.test($scope.submitData.server_ip))  
        {  
            $scope.setupForm.server_address.$setValidity("error", false);
            $('[name = "server_address"]').addClass('errorHighlight');
        } else {
            $scope.setupForm.server_address.$setValidity("error", true);
            $('[name = "server_address"]').removeClass('errorHighlight');
        }
    };

    $scope.getData = function() {
        if($scope.action == 'view' || $scope.action == 'edit') {
            var reqHeader = {
                appendToURL : true,
                value : dataToModal.id,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.aaa_server.view, null, reqHeader).then(function(data) {
                $scope.submitData = data;
            });
        }
    };

    $scope.init = function() {
        this.getData();
    }

    $scope.init();

});