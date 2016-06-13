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
    $scope.showDetails = false;

    $scope.searchSwitch = function() {
    	/*$scope.switch.availableData = {
		"switch_name": "s2",
		"boot_status": "Success",
		"serial_number": "s2",
		"discovery_rule": "['rule1', 'rule2']",
		"match_type": "Neighbor",
		"rule_id": "[1, 2]"
		}*/
        var reqHeader = {
            appendToURL : true,
            value : $scope.switch.reqData.old_serial_num,
            noTrailingSlash : true
        };
        
    	appServices.doAPIRequest(appSettings.appAPI.rma.search, null, reqHeader).then(function(data) {
           $scope.switch.availableData = data;
           $scope.mapDiscoveryRule();
           $scope.showDetails = true;
        });
    };

    $scope.isObjectEmpty = function(object) {
        if(object === undefined || object === null || object === '' || object.length === 0){
            return true;
        }
        return false;
    };

    $scope.mapDiscoveryRule = function() {
        $scope.showSwitchDetails = false;
        var rule_id = $scope.switch.availableData.rule;
        if(this.isObjectEmpty(rule_id)) {
            $scope.showSwitchDetails = true;
        }
        if(this.isObjectEmpty(rule_id) && 
            !this.isObjectEmpty($scope.switch.availableData.switch_detail) && 
                !this.isObjectEmpty($scope.switch.availableData.switch_detail.boot_detail) && 
                    $scope.switch.availableData.switch_detail.boot_detail.discovery_rule != 0) {
            rule_id = $scope.switch.availableData.switch_detail.boot_detail.discovery_rule;
        } else {
            $scope.switch.availableData.rule_name = '--';
        }
        if(rule_id != '') {
            $scope.discovery_rule_list.filter(function(a){
                if(a.id == rule_id) {
                    $scope.switch.availableData.rule_name = a.name;
                }
            })
        }
    };

    $scope.openRuleModal = function(id) {
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/ruleModal.html',
            controller: 'RuleModalCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        action : "external",
                        id : id,
                        configurations : $scope.configurations,
                        imglist : $scope.imglist,
                        workflow_list : $scope.workflow_list,
                        callerScope : $scope
                    }
                }
             }
        });

        $scope.modalInstance.result.then(function(modalData) {
            
        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });

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

    $scope.newSearch = function() {
        $scope.showDetails = false;
        $scope.switch.reqData.new_serial_num = '';
    };

    $scope.submitData = function(modalData) {
    	if(modalData.action == 'replace') {
    		//alert('replaced');
    		appServices.doAPIRequest(appSettings.appAPI.rma.replace, $scope.switch.reqData, null).then(function(data) {
                $scope.showDetails = false;
                $scope.switch.reqData.old_serial_num = '';
                var alertMsg = "Switch successfully replaced!";
                var modalInstance = $modal.open({
                    animation: $scope.animationsEnabled,
                    templateUrl: 'pages/template/modal/deleteModal.html',
                    controller: 'AlertModalCtrl',
                    size: 'md',
                    resolve: {
                        dataToModal : function() {
                            return {
                                id: $scope.selectedId,
                                action: 'info',
                                message: alertMsg,
                                callerScope: $scope
                            }
                        }
                     }
                });
	        });
    	}
    };

    $scope.cancel = function() {
        $location.path('fabricInstance');
    };

    $scope.init = function() {
        var reqHeader = {
                appendToURL: true,
                value: '?submit=true',
                noTrailingSlash: true
              };
        $scope.discovery_rule_list = [];
        appServices.doAPIRequest(appSettings.appAPI.discoveryRule.list, null, null).then(function(data) {
            $scope.discovery_rule_list = data;
        });
        appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, null).then(function(data) {
            $scope.configurations = data;
        });
        /*appServices.doAPIRequest(appSettings.appAPI.discoveryRule.list, null, null).then(function(data) {
            $scope.discoveryRules = data;
            $scope.getSwitchDetails();
        });*/
        appServices.doAPIRequest(appSettings.appAPI.images.list, null, null).then(function(data) {
          $scope.imglist = data;
        });
        appServices.doAPIRequest(appSettings.appAPI.workflow.list, null, reqHeader).then(function(data) {
          $scope.workflow_list = data;
        });
    }

    $scope.init();
});