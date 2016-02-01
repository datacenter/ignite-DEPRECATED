'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('PoolCtrl', function($scope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
        /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope)

        var parent = $scope.$parent;

        /**Pagination**/

        $scope.totalItems = 64;
        $scope.currentPage = 4;

        $scope.setPage = function(pageNo) {
            $scope.currentPage = pageNo;
        };

        $scope.pageChanged = function() {
            $log.log('Page changed to: ' + $scope.currentPage);
        };

        $scope.maxSize = 5;
        $scope.bigTotalItems = 175;
        $scope.bigCurrentPage = 1;
        /**./Pagination**/


        /**Configlets Modal**/

        $scope.animationsEnabled = true;
        $scope.pools = [];

        $scope.open = function(size) {

            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/poolsModal.html',
                controller: 'PoolsModalCtrl',
                size: size
            });

            modalInstance.result.then(function(selectedItem) {
                $scope.selected = selectedItem;
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });

        };

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
                appServices.tablePagination($defer, $filter, params, $scope.pools, $scope.searchKeyword);
            }
        });


        $scope.viewPool = function(size) {
            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/viewPoolModal.html',
                controller: 'ViewPoolCtrl',
                size: size
            });

            modalInstance.result.then(function(selectedItem) {
                $scope.selected = selectedItem;
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });

        };

        $scope.getPoolList = function(callback) {
          appServices.doAPIRequest(appSettings.appAPI.pools.list, null, null).then(function(data) {
              $scope.pools = data;
              $scope.totalPools = $scope.pools.length;
              $scope.tableParams.reload();
          });
        }

        /*$scope.getPoolById = function() {
          appServices.doAPIRequest(appSettings.appAPI.pools.)
        }*/

        $scope.checkAll = function () {
          if ($scope.selectedAll) {
              $scope.selectedAll = true;
              $scope.selection = $scope.pools.map(function(item){return item.id});
          } else {
              $scope.selectedAll = false;
              $scope.selection.length = 0;
          }
          angular.forEach($scope.pools, function (pool) {
              pool.Selected = $scope.selectedAll;
          });
        };

      // Fired when an pool in the table is checked
        $scope.selectPool = function () {
            // If any pool is not checked, then uncheck the "selectedAll" checkbox
            for (var i = 0; i < $scope.pools.length; i++) {
                if (!$scope.pools[i].isChecked) {
                    $scope.selectedAll = false;
                    return;
                }
            }

            // ... otherwise ensure that the "selectedAll" checkbox is checked
            $scope.selectedAll = true;
        };

        // For Pagination
        $scope.totalPools = 0;
        $scope.currentPage = 1;
        $scope.numPerPage = 10;

        $scope.paginate = function (value) {
          var begin, end, index;
          begin = ($scope.currentPage - 1) * $scope.numPerPage;
          end = begin + $scope.numPerPage;
          if (end >= $scope.totalPools) end = $scope.totalPools;
          $scope.begin = begin + 1;
          $scope.end = end;
          index = $scope.pools.indexOf(value);
          return (begin <= index && index < end);
        };

        // For Selection of Multiple Records
        $scope.selection=[];
        // toggle selection for a given employee by name
        $scope.toggleSelection = function (poolId) {
           var idx = $scope.selection.indexOf(poolId);

           // is currently selected
           if (idx > -1) {
             $scope.selection.splice(idx, 1);
           }

           // is newly selected
           else {
             $scope.selection.push(poolId);
           }
         };

         // For Deletion of Selected Pools
         $scope.deleteSelectedPool = function () {
           if ($scope.selection.length > 0) {
               var newPoolList = [];
               angular.forEach($scope.pools, function (pool) {
                 if (!pool.Selected) {
                   newPoolList.push(pool);
                 }
                 else {
                   appServices.doAPIRequest(appSettings.appAPI.pools.delete, null, null).then(function(data) {

                   });
                 }
               $scope.pools = newPoolList;
             });
           }
         }

         $scope.addPool = function() {
             $scope.action = "add";
             $scope.selectedId = null;
             $scope.openPoolModal();
         };

         $scope.viewPool = function(id) {
             $scope.action = "view";
             $scope.selectedId = id;
             $scope.openPoolModal();
         };

         $scope.editPool = function(id) {
             $scope.action = "edit";
             $scope.selectedId = id;
             $scope.openPoolModal();
         };

         $scope.deletePool = function(id, $index) {
             $scope.selectedId = id;

             var modalInstance = $modal.open({
                 animation: $scope.animationsEnabled,
                 templateUrl: 'pages/template/modal/deleteModal.html',
                 controller: 'AlertModalCtrl',
                 size: 'md',
                 resolve: {
                     dataToModal : function() {
                         return {
                             id : $scope.selectedId,
                             action: 'delete',
                             message: 'Are you sure you want to delete this pool?',
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
             $scope.toggleSelection($scope.selectedId);
             $scope.init();
         };



         /**Configlets Modal**/
         $scope.animationsEnabled = true;
         $scope.openPoolModal = function() {
             $scope.modalInstance = $modal.open({
                 animation: $scope.animationsEnabled,
                 templateUrl: 'pages/template/modal/poolsModal.html',
                 controller: 'PoolsModalCtrl',
                 size: 'lg',
                 backdrop: 'static',
                 resolve: {
                     dataToModal : function() {
                         return {
                             action : $scope.action,
                             id : $scope.selectedId,
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
                 appServices.doAPIRequest(appSettings.appAPI.pools.add, dataToSubmit, null).then(function(data) {
                    $scope.init();
                 });
             }

             else if(modalData.action == 'edit') {
                 var dataToSubmit = modalData.submitData;
                 var reqHeader = {
                     appendToURL : true,
                     value : $scope.selectedId,
                     noTrailingSlash : true
                 };
                 appServices.doAPIRequest(appSettings.appAPI.pools.edit, dataToSubmit, reqHeader).then(function(data) {
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

                 appServices.doAPIRequest(appSettings.appAPI.pools.delete, null, reqHeader).then(function(data) {
                     /* TODO after delete success */
                     $scope.init('delete');
                     $scope.modalInstance.dismiss();
                 });
             }
         };

        $scope.init = function() {
            $scope.getPoolList();
            //$scope.tableParams.reload();
        };

        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });

       $scope.checkboxes = { 'checked': false, items: {} };

        // watch for check all checkbox
        $scope.$watch('checkboxes.checked', function(value) {
            angular.forEach($scope.pools, function(item) {
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            });
        });

        // watch for data checkboxes
        $scope.$watch('checkboxes.items', function(values) {
            if (!$scope.pools) {
                return;
            }
            var checked = 0, unchecked = 0,
                    total = $scope.pools.length;
            angular.forEach($scope.pools, function(item) {
                checked   +=  ($scope.checkboxes.items[item.id]) || 0;
                unchecked += (!$scope.checkboxes.items[item.id]) || 0;
            });
            if ((unchecked == 0) || (checked == 0)) {
                $scope.checkboxes.checked = (checked == total);
            }
            // grayed checkbox
            angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
        }, true);

        $scope.init();

        $scope.toggleAnimation = function() {
            $scope.animationsEnabled = !$scope.animationsEnabled;
        };

        /**Configlets Modal**/
});

angular.module('PoapServer').controller('PoolsModalCtrl', function($scope, $modalInstance, $filter, ngTableParams, appSettings, appServices, dataToModal, $modal, $log) {
    $scope.appSettings = appSettings;
    $scope.appServices = appServices;
    $scope.action = dataToModal.action;

    $scope.totalItems = 64;
    $scope.currentPage = 4;

    $scope.maxSize = 5;
    $scope.bigTotalItems = 175;
    $scope.bigCurrentPage = 1;

    $scope.usedData = [];

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
            appServices.tablePagination($defer, $filter, params, $scope.usedData, $scope.searchKeyword);
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

    $scope.submitData = {
        "name":"",
        "type": "",
        "scope": appSettings.defaultData.pools.scope,
        "blocks": [{
            "start" : "",
            "end" : ""
        }]
    };

    $scope.ok = function() {
        var submitData = $scope.submitData;

        if($scope.action == 'edit') {
            submitData = $scope.submitData.blocks;
            submitData = submitData.filter(function(a) {
                if(a.noEdit != true) {
                    return a;
                }
            });
        }
        $modalInstance.close({
            submitData : submitData,
            action : $scope.action
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.getData = function(){
        if($scope.action ==  'view' || $scope.action == 'edit') {
            var requestHeader = {
                appendToURL : true, /* TODO - change to true in server */
                value : dataToModal.id,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.pools.getById, null, requestHeader).then(function(data) {
                debugger;
                $scope.submitData = data;
                $scope.submitData.blocks = $scope.submitData.blocks.filter(function(a){
                    a.noEdit = true;
                    return a;
                });
                $scope.usedData = data.entries;
                $scope.totalUsedData = $scope.usedData.length;
                $scope.tableParams.reload();
            });
        } else if($scope.appSettings.fieldValues.pools.types.length > 0){
            $scope.submitData.type = $scope.appSettings.fieldValues.pools.types[0].value;
        }
    };

    $scope.init = function() {
        $scope.getData();
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
        if(newAction == 'edit' && $scope.submitData.blocks.length == 0) {
            $scope.addRange();
        }
    }

    $scope.addRange = function() {
      $scope.submitData.blocks.push({start : '', end : ''});
    }

    $scope.removeRange = function($index) {
      $scope.submitData.blocks.splice($index, 1);
    }

    $scope.deletePool = function() {
      dataToModal.callerScope.deletePool(dataToModal.id, dataToModal.index);
    };

    $scope.checkAll = function(event) {
       $scope.isChecked = $(event.toElement).is(':checked');
    };

    $scope.init();
});

angular.module('PoapServer').controller('ViewPoolCtrl', function($scope, $modalInstance) {

    $scope.ok = function() {
        $modalInstance.close();
    };
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };
});
/*
angular.module('PoapServer').controller('PoolsDeleteModalCtrl',
    function($scope, $modalInstance, appSettings, appServices, dataToModal) {

    $scope.ok = function() {
        $modalInstance.close({
            action : 'delete',
            id : dataToModal.id,
            index : dataToModal.index
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

});*/
