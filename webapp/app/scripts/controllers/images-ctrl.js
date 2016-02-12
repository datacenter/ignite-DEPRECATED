'use strict';
/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */

angular.module('PoapServer')
    .controller('ImagesCtrl', function($scope, $location,$filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
    	/* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope);

        var parent = $scope.$parent;
        $scope.images = [];
        $scope.selectedId = null;

        $scope.addImages = function() {
			$scope.action = "add";
            $scope.selectedId = null;
            $scope.openImageModal();
        };

        $scope.cloneImage = function(id, index) {
            $scope.action = "clone";
            $scope.selectedId = id;
            $scope.openImageModal(index);
        };

        $scope.viewImage = function(id, index) {
            $scope.action = "view";
            $scope.selectedId = id;
            $scope.openImageModal(index);
        };

        $scope.editImage = function(id, index) {
            $scope.action = "edit";
            $scope.selectedId = id;
            $scope.openImageModal(index);
        };

        $scope.deleteImage = function(id, index) {
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
                            message: 'Are you sure you want to delete the image?',
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


        /**For table pagination**/
        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "image_profile_name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.images, $scope.searchKeyword);
            }
        });

        $scope.init = function(mode) {
            $scope.getImageList();
        };

        $scope.getImageList = function() {
            appServices.doAPIRequest(appSettings.appAPI.images.list, null, null).then(function(data) {
                console.log('*******************************************'+JSON.stringify(data)+'****************************************');
                $scope.images = data;
                $scope.tableParams.reload();
            });
        };

        /**Images Modal**/
        $scope.animationsEnabled = true;
        $scope.openImageModal = function(index) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/imagesModal.html',
                controller: 'ImagesModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : $scope.action,
                            callerScope : $scope,
                            id : $scope.selectedId,
                            index : index,
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
            if(modalData.action == 'add' || modalData.action == 'clone') {
                var dataToSubmit = modalData.submitData;
                var reqHeader = {};
                appServices.doAPIRequest(appSettings.appAPI.images.add, dataToSubmit, null).then(function(data) {
                   $scope.init();
                });
            }

            else if(modalData.action == 'edit') {
                var dataToSubmit = modalData.submitData;
                var editById = angular.copy(appSettings.appAPI.images.edit);
                editById.url = editById.url+$scope.selectedId;

                appServices.doAPIRequest(editById, dataToSubmit, null).then(function(data) {
                    /* TODO after delete success */
                    $scope.init('edit');
                    if(typeof $scope.modalInstance != 'undefined') {
                        $scope.modalInstance.dismiss();
                    }
                });
            }

            else if(modalData.action == 'delete') {

                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                appServices.doAPIRequest(appSettings.appAPI.images.delete, null, reqHeader).then(function(data) {
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

angular.module('PoapServer').controller('ImagesModalCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.error = "";
    $scope.formIncomplete = true;
    $scope.readonly = false;

    if(dataToModal.source != undefined) {
        $scope.readonly = true;
    }

    $scope.access_protocol_list = {
        "sftp": "sftp",
        "tftp": "tftp",
        "http": "http",
    	"scp": "scp"
    }

    $scope.submitData = {
        "profile_name":"",
        "image_name":"",
        "image_server_ip":"",
        "image_server_username":"",
        "image_server_password":"",
        "access_protocol": appSettings.defaultData.images.access_protocol
    };

    $scope.ok = function() {
        if(this.isObjectEmpty($scope.submitData.system_image)) {
            $scope.submitData.system_image = null;
        }
        if(this.isObjectEmpty($scope.submitData.epld_image)) {
            $scope.submitData.epld_image = null;
        }
        if(this.isObjectEmpty($scope.submitData.kickstart_image)) {
            $scope.submitData.kickstart_image = null;
        }
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            index : dataToModal.index
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.validateIPaddress = function()   
    {
        var ipPattern = /^([0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (!ipPattern.test($scope.submitData.image_server_ip))  
        {  
            $scope.imageForm.imageserver_ip.$setValidity("error", false);
        } else {
            $scope.imageForm.imageserver_ip.$setValidity("error", true);
        }
    };

    $scope.getData = function(){
        if($scope.action ==  'view' || $scope.action == 'edit'  || $scope.action == 'clone') {
            var getDataById = angular.copy(appSettings.appAPI.images.getById);
            getDataById.url = getDataById.url+dataToModal.id;
            appServices.doAPIRequest(getDataById, null, null).then(function(data) {
                $scope.submitData = data;
                if($scope.action == 'clone') {
                    $scope.submitData.profile_name = '';
                }
            });
        }
    };

    $scope.init = function() {
        $scope.getData();
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    };

    $scope.deleteImage = function() {
        dataToModal.callerScope.deleteImage(dataToModal.id, dataToModal.index);
    };

    $scope.isObjectEmpty = function(item) {
        if(item === undefined || item === null || item === '' || item.length === 0) {
            return true;
        }
        return false;
    };

    $scope.init();

});