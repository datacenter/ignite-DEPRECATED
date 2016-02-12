'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('UsersCtrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {

  	appServices.setInternalAppUI($scope);

    var parent = $scope.$parent;
    $scope.users = [];
    $scope.selectedId = null;

    $scope.addUser = function() {
        $scope.action = 'add';
        $scope.selectedId = null;
        this.openUserModal();
    };

    $scope.viewUser = function(id, index) {
        $scope.action = 'view';
        $scope.selectedId = id;
        this.openUserModal(index);
    };

    $scope.editUser = function(id, index) {
        $scope.action = 'edit';
        $scope.selectedId = id;
        this.openUserModal(index);
    };

    $scope.deleteUser = function(id) {
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
                        message: 'Are you sure you want to delete this user?',
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

    $scope.openUserModal = function(index) {
    	$scope.userModalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/userModal.html',
            controller: 'UserModalCtrl',
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

        $scope.userModalInstance.result.then(function(data) {
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
            appServices.doAPIRequest(appSettings.appAPI.aaa_user.add, modalData.submitData, null).then(function(data) {
               $scope.init();
            });
        } else if(modalData.action == 'delete') {
            appServices.doAPIRequest(appSettings.appAPI.aaa_user.delete, modalData.submitData, reqHeader).then(function(data) {
               $scope.init();
               /*if(typeof $scope.aaaModalInstance != 'undefined') {
                    $scope.aaaModalInstance.dismiss();
                }*/
            });
        } else if(modalData.action == 'edit') {
            appServices.doAPIRequest(appSettings.appAPI.aaa_user.edit, modalData.submitData, reqHeader).then(function(data) {
               $scope.init();
            });
        }
    };

    $scope.init = function() {
        $scope.getAAAuserList();
    };

    $scope.getAAAuserList = function() {
        appServices.doAPIRequest(appSettings.appAPI.aaa_user.list, null, null).then(function(data) {
            console.log('*******************************************'+JSON.stringify(data)+'****************************************');
            $scope.users = data;
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
            appServices.tablePagination($defer, $filter, params, $scope.users, $scope.searchKeyword);
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

angular.module('PoapServer').controller('UserModalCtrl',function($scope, $modalInstance, appServices, appSettings, dataToModal) {
	$scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.index = dataToModal.index;

    $scope.submitData = {
        username : '',
        email : '',
        password : '',
        is_superuser : false
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.verifyPwd = function() {
        if($scope.action == 'edit') {
            $scope.chPwd = true;
        }
    	if($scope.submitData.password !== $scope.submitData.vpwd) {
    		$scope.userForm.pwd.$setValidity("error", false);
    		$scope.userForm.vpwd.$setValidity("error", false);
    		$("[name='pwd'],[name='vpwd']").addClass('errorHighlight');
    	} else {
    		$scope.userForm.pwd.$setValidity("error", true);
    		$scope.userForm.vpwd.$setValidity("error", true);
    		$("[name='pwd'],[name='vpwd']").removeClass('errorHighlight');
    	}
    };

    $scope.validateEmailPattern = function() {
        var emailPattern = /^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$/i;
        if (!emailPattern.test($scope.submitData.email))  
        {
            $scope.userForm.email.$setValidity("error", false);
            $('[name = "email"]').addClass('errorHighlight');
        } else {
            $scope.userForm.email.$setValidity("error", true);
            $('[name = "email"]').removeClass('errorHighlight');
        }
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    };

    $scope.ok = function() {
        if(!$scope.chPwd) {
            $scope.submitData.password = $scope.submitData.vpwd = null;
        }
        if(!$scope.submitData.is_superuser) {
            $scope.submitData.is_superuser = !!$scope.submitData.is_superuser;
        }
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            index : dataToModal.index
        });
    };

    $scope.init = function() {
        $scope.chPwd = true;
        if($scope.action == 'view' || $scope.action == 'edit') {
            var reqHeader = {
                appendToURL : true,
                value : dataToModal.id,
                noTrailingSlash : true                 
            };
            appServices.doAPIRequest(appSettings.appAPI.aaa_user.view, null, reqHeader).then(function(data) {
                $scope.submitData = data;
                $scope.submitData.password = 'stars';
                $scope.submitData.vpwd = 'stars';
            });
            $scope.chPwd = false;
        }
    };

    $scope.init();

});