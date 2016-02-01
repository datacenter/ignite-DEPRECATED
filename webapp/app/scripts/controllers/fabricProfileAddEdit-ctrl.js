'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('FabricProfileAddEdit', function($scope, $location,$routeParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {
        /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope);
        var parent = $scope.$parent;
        $scope.checkbox = [];

        
        $scope.animationsEnabled = true;

        $scope.submitData = {
            "name": "",
            "submit"  : false,
            "construct_list"  : []
        };

        $scope.getProfileTemplateName = function(id) {
            var name = '';
            angular.forEach($scope.profile_templates, function(val, key) {
                if(val.id == id) {
                    name = val.name;
                    return false;
                }
            })

            return name;
        };

         $scope.getParamValue = function(type, value) {

            if(type != 'Pool') {
                return value;
            }

            var name = '';
            angular.forEach($scope.pools, function(val, key) {
                if(val.id == value) {
                    name = val.name;
                    return false;
                }
            })
            return name;
        };

        var checkPosition = function(positionHelper) {

            if(positionHelper == 'start') {
                return 0
            }

            else if(positionHelper == 'end') {
                return $scope.submitData.construct_list.length;
            }

            else if(positionHelper == 'before' || positionHelper == 'after') {
                var $checkboxes = $('#constructsList').find('.chk');
                var count = 0;
                var position = 0;
                $.each($checkboxes, function(key, val) {
                    if($(this).is(':checked') == true) {
                        count++;
                        position = key;
                    }
                })

                if(count == 0) {
                    alert('Select a row for this action.');
                    return false;
                }

                else if(count > 1) {
                    alert('More than one row cannot be selected for this action.');
                    return false;
                }


                if(positionHelper == 'before') {
                    return position;
                }

                else if(positionHelper == 'after') {
                    return position+1;
                }


            }

        }

        $scope.constructDialog = function(action, positionHelper, index) {

            var position = checkPosition(positionHelper);
            if(position === false) {
                return;
            }

            $scope.constructModalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/fabricProfileConstructModal.html',
                controller: 'FabricProfileConstructModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        var dtm = {
                            pools : $scope.pools,
                            profile_templates : $scope.profile_templates,
                            action : action,
                            position : position,
                            index : index,
                            mode : $scope.mode,
                            callerScope : $scope
                        };

                        if(action == 'view' || action == 'edit') {
                            dtm.editData = $scope.submitData.construct_list[index];
                        }

                        return dtm;
                    }
                 }
            });

            $scope.constructModalInstance.result.then(function(data) {
                $scope.addEditConstruct(data);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });

        };

        $scope.addEditConstruct = function(data) {
            if(data.action == 'add') {
                $scope.submitData.construct_list.splice(data.position, 0, data.submitData);
                //$scope.submitData.construct_list.push(data.submitData);
            }

            if(data.action == 'edit') {
                $scope.submitData.construct_list.splice(data.index, 1, data.submitData);
            }
        };

        $scope.submit = function() {
            $scope.submitData.submit = true;
            $scope.doSubmit();
        };

        $scope.save = function() {
            $scope.doSubmit();
        };

        $scope.doSubmit = function() {
            var mode = $routeParams.mode;
            console.log($scope.submitData);
            if(mode == 'add' || mode == 'clone') {

                appServices.doAPIRequest(appSettings.appAPI.fabricProfile.add, $scope.submitData, null).then(function(data) {
                    $location.path('/fabricProfile');
                });
            }
            else if(mode == 'edit') {
                var id = $routeParams.id;
                var reqHeader = {
                    appendToURL : true,
                    value : id,
                    noTrailingSlash : true
                };
                appServices.doAPIRequest(appSettings.appAPI.fabricProfile.edit, $scope.submitData, reqHeader).then(function(data) {
                    $location.path('/fabricProfile');
                });
            }

        };

        $scope.getPoolList = function() {
            appServices.doAPIRequest(appSettings.appAPI.pools.list, null, null).then(function(data) {
                $scope.pools = data;
            });
        };

        $scope.getProfileTemplateList = function() {
            appServices.doAPIRequest(appSettings.appAPI.profileTemplates.list, null, null).then(function(data) {
                $scope.profile_templates = data;
            });
        };

        $scope.toggleAnimation = function() {
            $scope.animationsEnabled = !$scope.animationsEnabled;
        };

        $scope.getFabricProfile = function(){
            var id = $routeParams.id;
            var reqHeader = {
                    appendToURL : true,
                    value : id,
                    noTrailingSlash : true
            };

            appServices.doAPIRequest(appSettings.appAPI.fabricProfile.view, null, reqHeader).then(function(data) {
                $scope.submitData = data;

                if($routeParams.mode == 'clone') {
                    $scope.submitData.name = "";
                }
            });

        };

        $scope.init = function(){
            $scope.getProfileTemplateList();
            $scope.getPoolList();
            $scope.mode = $routeParams.mode;
            $scope.configId = $routeParams.id;

            if($routeParams.mode == 'edit' ||  $routeParams.mode == 'view' ||  $routeParams.mode == 'clone') {
                $scope.getFabricProfile();
            }
        };

        $scope.goBack = function(path) {
            $location.path(path);
        };

        $scope.deleteFabricProfile = function(id, $index) {
            $scope.selectedId = $scope.configId;
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
                            message: 'Are you sure you want to delete the fabric profile?',
                            callerScope : $scope
                        }
                    }
                 }
            });

            modalInstance.result.then(function(modalData) {
                $scope.doDelete(modalData);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        $scope.doDelete = function() {
            var id = $routeParams.id;
            var reqHeader = {
                appendToURL : true,
                value : id,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.fabricProfile.delete, $scope.submitData, reqHeader).then(function(data) {
                $location.path('/fabricProfile');
            });
        };

        $scope.deleteConstruct = function($index) {
            var modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/deleteModal.html',
                controller: 'AlertModalCtrl',
                size: 'md',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            index : $index,
                            action: 'delete',
                            message: 'Are you sure you want to delete the construct?',
                            callerScope : $scope
                        }
                    }
                 }
            });

            modalInstance.result.then(function(modalData) {
                if(modalData.action == 'delete') {
                    $scope.doDeleteConstruct(modalData);
                }

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        };

        $scope.doDeleteConstruct = function(modalData){
            $scope.submitData.construct_list.splice(modalData.index, 1);
            $scope.constructModalInstance.dismiss();
        };

        $scope.ProfileTemplateDialog = function(id) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/profileTemplatesModal.html',
                controller: 'ProfileTemplatesModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : 'viewothers',
                            id : id
                        }
                    }
                 }
            });
        };

        $scope.init();
});



/*angular.module('PoapServer').controller('ConstructDeleteModalCtrl',
    function($scope, $modalInstance, appSettings, appServices, dataToModal) {
        $scope.ok = function() {
            $modalInstance.close({
                action : 'delete',
                index : dataToModal.index
            });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };
});*/


angular.module('PoapServer').controller('FabricProfileConstructModalCtrl', function($scope, $modalInstance, $modal, appServices, appSettings, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.params_list = [];
    $scope.action = dataToModal.action;

    $scope.submitData = {
        template_id : "",
        param_list : []
    };

    $scope.profile_templates = [];

    $scope.resetValues = function() {
        $scope.submitData.template_id = '';
        $scope.params_list = [];
    };


    $scope.filterParams = function() {
        debugger;
        $scope.params_list = [];
        $scope.submitData.param_list = [];
        angular.forEach($scope.profileTemplatesCache, function(val, key) {
            if(val.id == $scope.submitData.template_id) {
                angular.forEach(val.parameters, function(val1, key1) {
                    var paramObject = {
                        "param_name": val1,
                        "param_type": "Fixed",
                        "param_value": ""
                    };
                    $scope.params_list.push(paramObject);
                });
            }
        });
    };

    $scope.ok = function() {
        console.log($scope.submitData);
        $modalInstance.close({
            submitData : $scope.submitData,
            action : $scope.action,
            position : dataToModal.position,
            index : dataToModal.index
        });
    };
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.setValues = function() {
        setTimeout(function() {
            $scope.submitData.template_id = dataToModal.editData.template_id;
            angular.copy(dataToModal.editData.param_list, $scope.params_list);
            angular.copy(dataToModal.editData.param_list, $scope.submitData.param_list);
            $scope.$digest();
        }, 500);
    }

    $scope.init = function(){
        $scope.pools = dataToModal.pools;
        $scope.profileTemplatesCache = dataToModal.profile_templates;
        $scope.profile_templates = dataToModal.profile_templates;
        $scope.mode = dataToModal.mode;
        $scope.constructIndex = dataToModal.index;

        //$scope.submitData.construct_type = "append_template";

        if(dataToModal.action == 'view' || dataToModal.action == 'edit') {
            $scope.setValues();
        }
    };

    $scope.deleteConstruct = function($index){
        dataToModal.callerScope.deleteConstruct($index);
    };

    $scope.init();

});
