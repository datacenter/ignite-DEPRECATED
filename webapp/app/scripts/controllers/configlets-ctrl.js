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

        $scope.viewConfiglet = function(configletindex_id, id, index) {
            $scope.action = "view";
            $scope.selectedId = configletindex_id;
            $scope.openConfigletModal(id, index);
            /*var requestHeader = {
                appendToURL : true,
                value : configletindex_id,
                noTrailingSlash : true
            };

            appServices.doAPIRequest(appSettings.appAPI.configlets.getById, null, requestHeader).then(function(data) {
                    $scope.openConfigletModal(id, index, data);
            });*/
            
        };

        $scope.editConfiglet = function(id, index) {
            $scope.action = "edit";
            $scope.selectedId = id;
            $scope.openConfigletModal(index);
        };

        $scope.deleteConfiglet = function(configletindex_id, id, index) {
            $scope.selectedId = configletindex_id;
            $scope.latest_version = id;

            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/configletDelete.html',
                controller: 'ConfigDeleteCtrl',
                size: 'md',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            id : $scope.selectedId,
                            action : 'delete',
                            callerScope : $scope
                        }
                    }
                 }
            });

            modalInstance.result.then(function(modalData) {
                $scope.delete_type = modalData.submitData.delete_operation;
                $scope.deleteConfirm(modalData);

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        $scope.deleteConfirm = function(modalData) {
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
                            message : 'Are you sure you want to delete?',
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
        }



        /**Configlets Modal**/
        $scope.animationsEnabled = true;
        $scope.openConfigletModal = function(id, index) {
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
                            id : id,
                            configletindex_id : $scope.selectedId,
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
                value : data.append_url,
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
                        data.append_url = data.configletindex_id+'/true';
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
                        append_url : $scope.selectedId+"/configlet/"+modalData.submitData.id+"/"+modalData.new_version
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

                if($scope.delete_type === 'delete_latest') {
                    reqHeader.value = reqHeader.value+'/configlet/'+$scope.latest_version+'/none';
                } else {
                    reqHeader.value = reqHeader.value+'/none';
                }

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

angular.module('PoapServer').controller('ConfigletsModalCtrl', function($scope, $modal, $modalInstance, FileReader, appSettings, appServices, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    /*$scope.version_data = dataToModal.versions;
    $scope.version = dataToModal.id;*/
    $scope.latest_version = 1;
    $scope.version = "";

    $scope.readFile = function($fileContent){
        $scope.content = $fileContent;
    };

    $scope.submitData = {
        "name":"",
        "group":"",
        "type": appSettings.defaultData.configlets.config_type
    };

    $scope.save = function() {

        if($scope.action == 'edit' && $scope.version == $scope.latest_version) {
            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/configSave.html',
                controller: 'SaveConfigCtrl',
                size: 'md',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            callerScope : $scope
                        }
                    }
                 }
            });

            modalInstance.result.then(function(modalData) {
                $scope.ok(modalData);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        } else {
            var modalData = {
                new_version : false
            }
            $scope.ok(modalData);
        }
    };

    $scope.ok = function(modalData) {
        $modalInstance.close({
            submitData : $scope.submitData,
            uploadFile : $scope.uploadFile,
            new_version : modalData.new_version,
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
                value : dataToModal.configletindex_id+'/false',
                noTrailingSlash : true
            };
            /*+'/configlet/'+dataToModal.id
            appServices.doAPIRequest(appSettings.appAPI.configlets.getById, null, requestHeader).then(function(data) {
                    $scope.submitData = data;
                    $scope.version = 1;
                    $scope.view = {
                        fileContent : data.fileContent
                    }
            });

            requestHeader.value = dataToModal.configletindex_id;*/
            appServices.doAPIRequest(appSettings.appAPI.configlets.getById, null, requestHeader).then(function(data) {
                    $scope.version_data = data;
                    $scope.submitData = $scope.version_data[$scope.version_data.length - 1];
                    $scope.latest_version = $scope.submitData.version;
                    $scope.version = angular.copy($scope.latest_version);
                    if(dataToModal.version != undefined) {
                        $scope.version = dataToModal.version;
                    }
                    $scope.loadVersion();
            });
        }
    };

    $scope.loadVersion = function() {
        $scope.submitData = ($scope.version_data.filter(function(version) {
                    return version.version == $scope.version;
                }))[0];
        $scope.new_version = false;
        // alert('version : '+$scope.version);

    };

    $scope.init = function() {
        $scope.getData();

    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    }

    $scope.deleteConfiglet = function()  {
        dataToModal.callerScope.deleteConfiglet(dataToModal.configletindex_id, dataToModal.id, dataToModal.index);
    }

    $scope.init();
});


angular.module('PoapServer').controller('ConfigDeleteCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {
    $scope.submitData = {
      "delete_operation" : "delete_latest"
    }

    $scope.ok = function() {
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

    $scope.init();
  });