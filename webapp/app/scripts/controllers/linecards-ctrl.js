'use strict';
/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */


angular.module('PoapServer')
    .controller('LinecardCtrl', function($scope, $location,$filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {

		/* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope);

        var parent = $scope.$parent;
        $scope.switches = [];

    	$scope.init = function(mode) {
            $scope.getLinecardList();
        };

        $scope.tableParams = new ngTableParams({
            page: 1,
            count: appSettings.tableSettings.count,
            sorting: {
                "name": "asc"
            }
        }, {
            counts:[],
            getData: function($defer, params) {
                appServices.tablePagination($defer, $filter, params, $scope.switches, $scope.searchKeyword);

            }
        });

        $scope.selectedId = null;

        $scope.getLinecardList = function() {
            appServices.doAPIRequest(appSettings.appAPI.linecard.list, null, null).then(function(data) {
                $scope.switches = data;
                console.log(JSON.stringify(data));
                $scope.tableParams.reload();
            });
        };

        $scope.addLinecard = function() {
        	$scope.action = "add";
            $scope.selectedId = null;
            $scope.openLinecardModal();
        };

        $scope.editSwitch = function(id, index) {
            $scope.action = "edit";
            $scope.selectedId = id;
            $scope.openLinecardModal(index);
        };

        $scope.viewSwitch = function(id, index) {
            $scope.action = "view";
            $scope.selectedId = id;
            $scope.openLinecardModal(index);
        };

        $scope.deleteSwitch = function(id, index) {
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
                            message: 'Are you sure you want to delete?',
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

        $scope.submitData = function(modalData) {
            /* this is for add */
            if(modalData.action == 'add') {
                var dataToSubmit = modalData.submitData;
                console.log(dataToSubmit);
                appServices.doAPIRequest(appSettings.appAPI.linecard.add, dataToSubmit, null).then(function(data) {
                   $scope.init('add');
                });
            }

            else if(modalData.action == 'edit') {
                var dataToSubmit = modalData.submitData;
                console.log(dataToSubmit);
                var setDataById = angular.copy(appSettings.appAPI.linecard.edit);
                setDataById.url = setDataById.url+$scope.selectedId;
                appServices.doAPIRequest(setDataById, dataToSubmit, null).then(function(data) {
                   $scope.init('edit');
                });
            }

            else if(modalData.action == 'delete') {
                var reqHeader = {
                    appendToURL : true,
                    value : $scope.selectedId,
                    noTrailingSlash : true
                };

                appServices.doAPIRequest(appSettings.appAPI.linecard.delete, null, reqHeader).then(function(data) {
                    /* TODO after delete success */
                    $scope.init('delete');
                    if(typeof $scope.modalInstance != 'undefined') {
                        $scope.modalInstance.dismiss();
                    }
                });
            }
        };

        /**Switch Modal**/
        $scope.animationsEnabled = true;
        $scope.openLinecardModal = function(index) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/addLCModal.html',
                controller: 'LC_ModalCtrl',
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

        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });
        $scope.init();
    });
   

    
    /*

    Modal Controllers

*/

angular.module('PoapServer').controller('LC_ModalCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.fieldErr = false;

    $scope.domainValues = {
        tier_list : ['Core','Spine','Leaf','Host'],
        port_speed_list : ['1/10G' , '40G', '100G'],
        transceiver_list : ['GBASE-T', 'SFP+', 'QSFP+', 'QSFP28', 'CFP2'],
        port_role_list : ['Uplink','Downlink','Both']
    };

    $scope.port_group_structure = {
        "num_ports": 1,
        "speed": appSettings.defaultData.switches.port_speed,
        "transceiver" : appSettings.defaultData.switches.transceiver,
        "role": appSettings.defaultData.switches.port_role
    };

    $scope.submitData = {
        "name": "",
        "lc_type": "Linecard",
        "lc_data": {
            "port_groups": [
                {
                "num_ports": 1,
                "speed": appSettings.defaultData.switches.port_speed,
                "transceiver" : appSettings.defaultData.switches.transceiver,
                "role": appSettings.defaultData.switches.port_role
                }
            ]
        }
    };

    $scope.addPortGrp = function() {
        var new_portGrp = angular.copy($scope.port_group_structure);
        $scope.submitData.lc_data.port_groups.push(new_portGrp);
    };

    $scope.delPortGrp = function(index) {
        $scope.submitData.lc_data.port_groups.splice(index,1);
    };

    $scope.isObjectEmpty = function(object) {
        if(object === undefined || object === null || object === '' || object.length === 0){
            return true;
        }
        return false;
    };

    $scope.checkModelName = function() {
        if(this.isObjectEmpty($scope.submitData.name)){
            $scope.lc_form.name.$setValidity("error", false);
        } else {
            $scope.lc_form.name.$setValidity("error", true);
        }
    };

    $scope.checkTierRoles = function() {
        if(this.isObjectEmpty($scope.submitData.model_data.tier_roles)){
            $scope.lc_form.tier_roles.$setValidity("error", false);
        } else {
            $scope.lc_form.tier_roles.$setValidity("error", true);
        }
    };

    $scope.addModule = function() {
        var new_module = angular.copy($scope.module_structure);
        $scope.submitData.model_data.modules.push(new_module);
    };

    $scope.checkNumPorts = function(index) {
        if($scope.submitData.lc_data.port_groups[index].num_ports < 1){
            $scope.submitData.lc_data.port_groups[index].num_ports = 1;
        }
    };

    $scope.removeModule = function(index) {
        if($scope.submitData.model_data.modules.length > 0){
            $scope.submitData.model_data.modules.splice(index,1);
        }
    };

    $scope.checkSwitchValidity = function() {
        if(this.isObjectEmpty($scope.submitData.model_name)){
            $scope.lc_form.model_name.$setValidity("error", false);
        } else {
            $scope.lc_form.model_name.$setValidity("error", true);
        }

        if(this.isObjectEmpty($scope.submitData.model_data.tier_roles)){
            $scope.lc_form.tier_roles.$setValidity("error", false);
        } else {
            $scope.lc_form.tier_roles.$setValidity("error", true);
        }
    };

    $scope.ok = function() {
        /*if(this.isObjectEmpty($scope.submitData.model_data.tier_roles) || this.isObjectEmpty($scope.submitData.modules)) {
            $scope.fieldErr = true;
            $
        } else {*/
            $modalInstance.close({
                submitData : $scope.submitData,
                action : $scope.action
            });
        /*}*/
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.getData = function(){
       if($scope.action ==  'view' || $scope.action == 'edit'  || $scope.action == 'viewothers') {
            var getDataById = angular.copy(appSettings.appAPI.linecard.getById);
            getDataById.url = getDataById.url+dataToModal.id;
            appServices.doAPIRequest(getDataById, null, null).then(function(data) {
                $scope.submitData = data;
                console.log(data+" ************************************************** ********")
            });
        }
    };

    $scope.init = function() {
        $scope.getData();
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
    };

    $scope.deleteSwitch = function() {
        dataToModal.callerScope.deleteSwitch(dataToModal.id, dataToModal.index);
    };

    $scope.init();
});

/*angular.module('PoapServer').controller('LC_DeleteModalCtrl',
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