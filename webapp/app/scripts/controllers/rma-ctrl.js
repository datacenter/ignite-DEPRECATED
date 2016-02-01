'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('RMA_Ctrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {

    appServices.setInternalAppUI($scope);
    $scope.switch = {
    	reqData : {},
    	availableData : {}
    };

    $scope.searchSwitch = function() {
    	$scope.switch.availableData = {
		"switch_name": "s2",
		"boot_status": "Success",
		"serial_number": "s2",
		"discovery_rule": "['rule1', 'rule2']",
		"match_type": "Neighbor",
		"rule_id": "[1, 2]"
		}
    	/*appServices.doAPIRequest(appSettings.appAPI.rma.search, $scope.switch.reqData, null).then(function(data) {
           $scope.switch.availableData = data;
        });*/
    };

    $scope.warnReplace = function() {
    	var alertMsg = "Are you sure you want to replace switch - "+$scope.switch.reqData.old_serial_num+" with switch - "+$scope.switch.reqData.new_serial_num+"?";
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        id: $scope.selectedId,
                        action: 'replace',
                        message: alertMsg,
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

    $scope.submitData = function(modalData) {
    	if(modalData.action == 'replace') {
    		alert('replaced');
    		/*appServices.doAPIRequest(appSettings.appAPI.rma.replace, $scope.switch.reqData, null).then(function(data) {
	           $scope.switch.availableData = data;
	        });*/
    	}
    };
});