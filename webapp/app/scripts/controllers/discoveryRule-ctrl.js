'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('DiscoveryRuleCtrl', function($scope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
        /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope)

        var parent = $scope.$parent;

        /**Pagination**/

        $scope.totalItems = 64;
        $scope.currentPage = 4;

        $scope.maxSize = 5;
        $scope.bigTotalItems = 175;
        $scope.bigCurrentPage = 1;

        $scope.animationsEnabled = true;
        $scope.discoveryRules = [];

        $scope.animationsEnabled = true;

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "name": "asc"
            },
            filter : {
                name : $scope.searchKeyword
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                console.log($scope.searchKeyword);
                appServices.tablePagination($defer, $filter, params, $scope.discoveryRules, $scope.searchKeyword);
            }
        });

        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });

        $scope.setPage = function(pageNo) {
            $scope.currentPage = pageNo;
        };

        $scope.pageChanged = function() {
            $log.log('Page changed to: ' + $scope.currentPage);
        };

        $scope.checkAll = function(event) {
           $scope.isChecked = $(event.toElement).is(':checked');
        };

        $scope.toggleAnimation = function() {
            $scope.animationsEnabled = !$scope.animationsEnabled;
        };

        $scope.getDiscoveryRule = function(callback) {
            appServices.doAPIRequest(appSettings.appAPI.discoveryRule.list, null, null).then(function(data) {
                $scope.discoveryRules = data;
                $scope.totalDiscoveryRules = $scope.discoveryRules.length;
                $scope.tableParams.reload();
            });
        };

        $scope.getConfigurationDetailLists = function() {
          var reqHeader = {
            appendToURL: true,
            value: '?submit=true',
            noTrailingSlash: true
          };
            appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, null).then(function(data) {
                $scope.configurations = data;
            });
            appServices.doAPIRequest(appSettings.appAPI.images.list, null, null).then(function(data) {
              $scope.imglist = data;
            });
            appServices.doAPIRequest(appSettings.appAPI.workflow.list, null, reqHeader).then(function(data) {
              $scope.workflow_list = data;
            });
        };

        $scope.addRule = function() {
            $scope.action = "add";
            $scope.selectedId = null;
            $scope.openRuleModal();
        };

        $scope.viewRule = function(id) {
            $scope.action = "view";
            $scope.selectedId = id;
            $scope.openRuleModal();
        };

        $scope.editRule = function(id) {
            $scope.action = "edit";
            $scope.selectedId = id;
            $scope.openRuleModal();
        };

        $scope.deleteRule = function(id, $index) {
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
                            message: 'Are you sure you want to delete this discovery rule?',
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
            $scope.init();
        };

        /**Discovery Rule Modal**/
        $scope.openRuleModal = function(size) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/ruleModal.html',
                controller: 'RuleModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : $scope.action,
                            id : $scope.selectedId,
                            configurations : $scope.configurations,
                            imglist : $scope.imglist,
                            workflow_list : $scope.workflow_list,
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
            /* this is for add */
            if(modalData.action == 'add') {
                var dataToSubmit = modalData.submitData;
                var reqHeader = {};
                appServices.doAPIRequest(appSettings.appAPI.discoveryRule.add, dataToSubmit, null).then(function(data) {
                   $scope.init();
                });
            }

            else if(modalData.action == 'edit') {
                var dataToSubmit = modalData.submitData;
                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId
                };
                appServices.doAPIRequest(appSettings.appAPI.discoveryRule.edit, dataToSubmit, reqHeader).then(function(data) {
                    console.log(data);
                    $scope.init();
                });
            }

            else if(modalData.action == 'delete') {

                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                appServices.doAPIRequest(appSettings.appAPI.discoveryRule.delete, null, reqHeader).then(function(data) {
                    /* TODO after delete success */
                    $scope.init('delete');
                    $scope.modalInstance.dismiss();
                });
            }
        };

        $scope.init = function() {
            $scope.getConfigurationDetailLists();
            $scope.getDiscoveryRule();
        };

        $scope.init();
        /**Modal**/
});

angular.module('PoapServer').controller('RuleModalCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {
  $scope.appSettings = appSettings;
  $scope.action = dataToModal.action;
  $scope.configurations = angular.copy(dataToModal.configurations);
  $scope.imglist = angular.copy(dataToModal.imglist);
  $scope.workflow_list = angular.copy(dataToModal.workflow_list);
  var defaultVal = {"id" : 0, "name" : "--None--"};

  $scope.submitData = {
      "name" : "",
      "priority" : appSettings.defaultData.discoveryRule.priority,
      "config" : appSettings.defaultData.discoveryRule.buildConfigurationId,
      "match" : appSettings.defaultData.discoveryRule.match,
      "image" : "",
      "workflow" : 0,
      "subrules" : [{
        "rn_condition" : appSettings.defaultData.discoveryRule.rnCondition,
        "rn_string" : "",
        "rp_condition" : appSettings.defaultData.discoveryRule.rpCondition,
        "rp_string" : "",
        "lp_condition" : appSettings.defaultData.discoveryRule.lpCondition,
        "lp_string" : ""
      }],
      "subrules_serial_num" : ['']
  };


  $scope.ok = function() {
    $scope.submitData.subrules = $scope.submitData.subrules.filter(function(a){
      if('--N/A--' == a.rn_string){
        a.rn_string = '';
      }
      if('--N/A--' == a.rp_string){
        a.rp_string = '';
      }
      if('--N/A--' == a.lp_string){
        a.lp_string = '';
      }
      return a;
    });
      if($scope.submitData.match == 'serial_num') {
          $scope.submitData.subrules = $scope.submitData.subrules_serial_num;
          delete $scope.submitData.subrules_serial_num;
      }

      $modalInstance.close({
          submitData : $scope.submitData,
          action : $scope.action
      });
  };

  $scope.cancel = function() {
      $modalInstance.dismiss('cancel');
  };

  $scope.getData = function(){
      if($scope.action ==  'view' || $scope.action == 'edit' || $scope.action == 'external') {
          var requestHeader = {
              appendToURL : true,
              value : dataToModal.id
          };
          appServices.doAPIRequest(appSettings.appAPI.discoveryRule.getById, null, requestHeader).then(function(data) {
              $scope.submitData = data;
              if(data.workflow == null) {
                data.workflow = 0;
              }
              $scope.submitData.subrules = $scope.submitData.subrules.filter(function(a){
                if('' == a.rn_string){
                  a.rn_string = '--N/A--';
                }
                if('' == a.rp_string){
                  a.rp_string = '--N/A--';
                }
                if('' == a.lp_string){
                  a.lp_string = '--N/A--';
                }
                return a;
              });
              if($scope.submitData.match == 'serial_num') {
                  $scope.submitData.subrules_serial_num = $scope.submitData.subrules;
              }
          });
      }
  };

  $scope.init = function() {
      $scope.workflow_list.unshift(defaultVal);
      $scope.getData();
  };

  $scope.changeAction = function(newAction) {
      $scope.action = newAction;
  };

  $scope.addSubRule = function() {
      $scope.submitData.subrules.push({
        rn_condition : appSettings.defaultData.discoveryRule.rnCondition,
        rn_string : '',
        rp_condition : appSettings.defaultData.discoveryRule.rpCondition,
        rp_string : '',
        lp_condition : appSettings.defaultData.discoveryRule.lpCondition,
        lp_string : ''
      });
  };

  $scope.checkMatch = function(key, value, index) {
    if('any' == key) {
      $scope.submitData.subrules[index][value] = '--N/A--';
    } else {
      $scope.submitData.subrules[index][value] = '';
    }
  };

  $scope.addSubRuleSerialID = function() {
    $scope.submitData.subrules_serial_num.push('');
  };

  $scope.removeSubRule = function($index) {
    $scope.submitData.subrules.splice($index, 1);
  };

  $scope.removeSubRuleSerialID = function($index) {
    $scope.submitData.subrules_serial_num.splice($index, 1);
  };

  $scope.deleteRule = function() {
    dataToModal.callerScope.deleteRule(dataToModal.id, dataToModal.index);
  };

  $scope.init();
});
