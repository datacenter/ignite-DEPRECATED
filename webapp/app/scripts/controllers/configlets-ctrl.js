'use strict';
/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */

angular.module('PoapServer')
    .controller('ConfigletsCtrl', function($scope, $location,$filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
        /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope)

        var parent = $scope.$parent;
        $scope.configlets = [];

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.configlets, $scope.searchKeyword);

            }
        });

        $scope.selectedId = null;

        $scope.init = function(mode) {
            $scope.getConfigletList();
        };



        $scope.getConfigletList = function() {
            appServices.doAPIRequest(appSettings.appAPI.configlets.list, null, null).then(function(data) {
                //callback.call(this, data)
                $scope.configlets = data;
                $scope.tableParams.reload();
            });
        };



        $scope.addConfiglet = function() {
            $scope.action = "add";
            $scope.selectedId = null;
            $scope.openConfigletModal();
        };

        $scope.viewConfiglet = function(id, index) {
            $scope.action = "view";
            $scope.selectedId = id;
            $scope.openConfigletModal(index);
        };

        $scope.editConfiglet = function(id, index) {
            $scope.action = "edit";
            $scope.selectedId = id;
            $scope.openConfigletModal(index);
        };

        $scope.deleteConfiglet = function(id, index) {
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
                            action : 'delete',
                            message : 'Are you sure you want to delete this configlet?',
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
        };



        /**Configlets Modal**/
        $scope.animationsEnabled = true;
        $scope.openConfigletModal = function(index) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/configletsModal.html',
                controller: 'ConfigletsModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : $scope.action,
                            id : $scope.selectedId,
                            callerScope : $scope,
                            index : index
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



        $scope.uploadConfigletFile = function(data, file, callback) {
            var requestHeader = {
                fileUpload : true,
                appendToURL : true,
                value : data.id,
                noTrailingSlash : true
            };
            var dataToSubmit = file;
            appServices.doAPIRequest(appSettings.appAPI.configlets.upload, dataToSubmit, requestHeader).then(function(data) {
                callback.call(this, data)
            });
        };

        $scope.submitData = function(modalData) {
            /* this is for add */
            if(modalData.action == 'add') {
                var dataToSubmit = modalData.submitData;
                var reqHeader = {};
                appServices.doAPIRequest(appSettings.appAPI.configlets.add, dataToSubmit, null).then(function(data) {
                   if(typeof modalData.uploadFile != 'undefined') {
                        $scope.uploadConfigletFile(data, modalData.uploadFile, function(cData) {
                            console.log(cData);
                            $scope.init();
                        });
                   }
                   else  {
                        $scope.init();
                   }
                });
            }

            else if(modalData.action == 'edit') {
                if(typeof modalData.uploadFile != "undefined") {

                    var uData = {
                        id : $scope.selectedId
                    }

                    $scope.uploadConfigletFile(uData, modalData.uploadFile, function(cData) {
                            console.log(cData);
                            $scope.init();
                    });
                }

            }

            else if(modalData.action == 'delete') {

                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                appServices.doAPIRequest(appSettings.appAPI.configlets.delete, null, reqHeader).then(function(data) {
                    /* TODO after delete success */
                    $scope.init('delete');
                    if(typeof $scope.modalInstance != 'undefined') {
                        $scope.modalInstance.dismiss();
                    }
                });
            }
        };

        $scope.toggleAnimation = function() {
            $scope.animationsEnabled = !$scope.animationsEnabled;
        };

        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });

        $scope.init();
});


/*

    Modal Controllers

*/

angular.module('PoapServer').controller('ConfigletsModalCtrl', function($scope, $modalInstance, FileReader, appSettings, appServices, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;

    $scope.readFile = function($fileContent){
        $scope.content = $fileContent;
    };

    $scope.submitData = {
        "name":"",
        "group":""/*,
        "config_type": appSettings.defaultData.configlets.config_type*/
    };

    $scope.ok = function() {
        $modalInstance.close({
            submitData : $scope.submitData,
            uploadFile : $scope.uploadFile,
            action : $scope.action
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.getData = function(){
        if($scope.action ==  'view' || $scope.action == 'edit'  || $scope.action == 'viewothers') {
            var requestHeader = {
                appendToURL : true,
                value : dataToModal.id,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.configlets.getById, null, requestHeader).then(function(data) {
                $scope.submitData = data;
                $scope.view = {
                    fileContent : data.fileContent
                }
            });
        }
    };

    $scope.init = function() {
        $scope.getData();

    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    }

    $scope.deleteConfiglet = function()  {
        dataToModal.callerScope.deleteConfiglet(dataToModal.id, dataToModal.index);
    }

    $scope.init();
});