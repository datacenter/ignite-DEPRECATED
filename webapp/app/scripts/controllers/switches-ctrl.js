'use strict';
/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */


angular.module('PoapServer')
    .controller('SwitchesCtrl', function($scope, $location,$filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService) {

		/* When we enter tha app we need to remove the background from the login page and include headers and footers*/
        appServices.setInternalAppUI($scope);

        var parent = $scope.$parent;
        $scope.switches = [];

    	$scope.init = function(mode) {
            $scope.getSwitchList();
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

        $scope.getSwitchList = function() {
            appServices.doAPIRequest(appSettings.appAPI.switches.list, null, null).then(function(data) {
                $scope.switches = data;
                console.log(JSON.stringify(data));
                $scope.tableParams.reload();
            });
        };

        $scope.addSwitches = function() {
        	$scope.action = "add";
            $scope.selectedId = null;
            $scope.openSwitchModal();
        };

        $scope.editSwitch = function(id, index) {
            $scope.action = "edit";
            $scope.selectedId = id;
            $scope.openSwitchModal(index);
        };

        $scope.viewSwitch = function(id, index) {
            $scope.action = "view";
            $scope.selectedId = id;
            $scope.openSwitchModal(index);
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
                            message: 'Are you sure you want to delete this switch?',
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

        $scope.fetchSwitchStatus = function(status,swich) {
            if(swich[status] == 0) {
                return false;
            }
            var switch_stat = '';
            switch(status)
            {
                case 'booted_with_success' : switch_stat = 'success';
                                          break;
                case 'boot_in_progress' : switch_stat = 'progress';
                                          break;
                case 'booted_with_fail' : switch_stat = 'fail';
                                          break;
            }

            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/switchStatusList.html',
                controller: 'SwitchStatusModalCtrl',
                size: 'lg',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            status : switch_stat,
                            id : swich.id,
                            callerScope : $scope
                        }
                    }
                 }
            });
            
            /**/
        };

        $scope.submitData = function(modalData) {
            /* this is for add */
            if(modalData.action == 'add') {
                var dataToSubmit = modalData.submitData;
                console.log(dataToSubmit);
                appServices.doAPIRequest(appSettings.appAPI.switches.add, dataToSubmit, null).then(function(data) {
                   $scope.init('add');
                });
            }

            else if(modalData.action == 'edit') {
                var dataToSubmit = modalData.submitData;
                console.log(dataToSubmit);
                var setDataById = angular.copy(appSettings.appAPI.switches.edit);
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

                appServices.doAPIRequest(appSettings.appAPI.switches.delete, null, reqHeader).then(function(data) {
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
        $scope.openSwitchModal = function(index) {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/addSwitchModal.html',
                controller: 'SwitchModalCtrl',
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

angular.module('PoapServer').controller('SwitchModalCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {
    $scope.appSettings = appSettings;
    $scope.action = dataToModal.action;
    $scope.fieldErr = false;

    $scope.domainValues = {
        tier_list : ['Core','Spine','Leaf','Border'],
        port_speed_list : ['1/10G', '40G','100G'],
        transceiver_list : ['GBASE-T', 'SFP+', 'QSFP+', 'QSFP28', 'CFP2'],
        port_role_list : ['Uplink','Downlink','Both']
    };

    $scope.slot_max = 0;

    $scope.port_group_structure = {
        "num_ports": 1,
        "speed": appSettings.defaultData.switches.port_speed,
        "transceiver" : appSettings.defaultData.switches.transceiver,
        "role": appSettings.defaultData.switches.port_role
    };

    $scope.slot_structure = {
        "slot_num" : "",
        "lc_id" : ""
    };

    $scope.submitData = {
        "name": "",
        "switch_type": "Fixed",
        "switch_data": {
            "tiers" : [],
            "num_slots" : 1,
            "slots" : [
                {
                    "slot_num" : 1,
                    "lc_id" : ""
                }
            ],
            "port_groups": [
                {
                "num_ports": 1,
                "speed": appSettings.defaultData.switches.port_speed,
                "transceiver" : appSettings.defaultData.switches.transceiver,
                "role": appSettings.defaultData.switches.port_role
                }
            ],
            "module_id" : "0"
        }
    };

    $scope.addPortGrp = function() {
        var new_portGrp = angular.copy($scope.port_group_structure);
        $scope.submitData.switch_data.port_groups.push(new_portGrp);
    };

    $scope.delPortGrp = function(index) {
        $scope.submitData.switch_data.port_groups.splice(index,1);
    };

    $scope.addLC = function() {
        if($scope.submitData.switch_data.slots.length < $scope.submitData.switch_data.num_slots){
            var new_LC = angular.copy($scope.slot_structure);
            if(!this.isObjectEmpty($scope.module_list)){
                new_LC.lc_id = $scope.module_list[0].id;
            }
            $scope.submitData.switch_data.slots.push(new_LC);
        }
    };

    $scope.delLC = function(index) {
        $scope.submitData.switch_data.slots.splice(index,1);
    };

    $scope.checkSlotLen = function(){
        this.findMax();
        if($scope.submitData.switch_data.slots.length > $scope.submitData.switch_data.num_slots){
            $scope.submitData.switch_data.num_slots = $scope.submitData.switch_data.slots.length;
        }
        if($scope.slot_max > $scope.submitData.switch_data.num_slots) {
            $scope.switchForm.num_slots.$setValidity("error",false);
        } else {
            $scope.switchForm.num_slots.$setValidity("error",true);
        }
    };

    $scope.checkType = function(type) {
        if(type === 'fixed' && this.isObjectEmpty($scope.submitData.switch_data.port_groups)){
            $scope.submitData.switch_data.port_groups = [];
            $scope.addPortGrp();
            $scope.submitData.switch_data.module_id = "0";            
        } else if(type === 'chassis' && this.isObjectEmpty($scope.submitData.switch_data.slots)){
            $scope.submitData.switch_data.slots = [];
            $scope.submitData.switch_data.num_slots = 1;
            this.addLC();
            $scope.submitData.switch_data.slots[0].slot_num=1;
        }
    };

    $scope.findMax = function(){
        var max = $scope.submitData.switch_data.slots[0].slot_num;
        for(var i = 1; i<$scope.submitData.switch_data.slots.length; i++){
            if($scope.submitData.switch_data.slots[i].slot_num > max){
                max = $scope.submitData.switch_data.slots[i].slot_num;
            }
        }
        $scope.slot_max = max;
    };

    $scope.checkSlotNum = function(index) {
        /*if($scope.submitData.switch_data.slots[index].slot_num > $scope.submitData.switch_data.num_slots){
            $scope.switchForm['slot_num_'+index].$setValidity("error", false);
        } else {
            $scope.switchForm['slot_num_'+index].$setValidity("error", true);
        }*/
        if($scope.submitData.switch_data.slots[index].slot_num < 1){
            $scope.submitData.switch_data.slots[index].slot_num = 1;
        }
        this.findMax();
        if($scope.slot_max > $scope.submitData.switch_data.num_slots) {
            $scope.switchForm.num_slots.$setValidity("error",false);
        } else {
            $scope.switchForm.num_slots.$setValidity("error",true);
        }
    };

    $scope.checkPortGrpNum = function(index, indicator){
        var module_port_group_num = $scope.submitData.model_data.modules[index].module_port_group_num;
        var existingGrpNum = $scope.submitData.model_data.modules[index].port_groups.length;

        if(indicator !== undefined && isNaN(indicator)){
            $scope.submitData.model_data.modules[index].module_port_group_num = 
                module_port_group_num = module_port_group_num + 1;
        } else if(indicator !== undefined && existingGrpNum > 1 && existingGrpNum > indicator){
            $scope.submitData.model_data.modules[index].port_groups.splice(indicator,1);
            $scope.submitData.model_data.modules[index].module_port_group_num = 
                module_port_group_num = module_port_group_num - 1;
            return;
        }

        if(module_port_group_num < 1) {
            $scope.submitData.model_data.modules[index].module_port_group_num = 1;
        } 
        if(module_port_group_num > existingGrpNum) {
            var reqGrps = module_port_group_num - existingGrpNum;
            for(var i = 0; i < reqGrps; i++){
                var new_portGrp = angular.copy($scope.port_group_structure);
                $scope.submitData.model_data.modules[index].port_groups.push(new_portGrp);
            }
        } else if(module_port_group_num < existingGrpNum) {
            var remGrps = existingGrpNum - module_port_group_num;
            for(var i = 0; i < remGrps; i++){
                $scope.submitData.model_data.modules[index].port_groups.pop();
            }
        }
    };

    $scope.isObjectEmpty = function(object) {
        if(object === undefined || object === null || object === '' || object.length === 0){
            return true;
        }
        return false;
    };

    $scope.checkModelName = function() {
        if(this.isObjectEmpty($scope.submitData.name)){
            $scope.switchForm.name.$setValidity("error", false);
        } else {
            $scope.switchForm.name.$setValidity("error", true);
        }
    };

    $scope.checkTierRoles = function() {
        if(this.isObjectEmpty($scope.submitData.switch_data.tiers)){
            $scope.switchForm.tiers.$setValidity("required", false);
        } else {
            $scope.switchForm.tiers.$setValidity("required", true);
        }
    };

    $scope.addModule = function() {
        var new_module = angular.copy($scope.module_structure);
        $scope.submitData.model_data.modules.push(new_module);
    };

    $scope.removeModule = function(index) {
        if($scope.submitData.model_data.modules.length > 0){
            $scope.submitData.model_data.modules.splice(index,1);
        }
    };

    $scope.checkSwitchValidity = function() {
        if(this.isObjectEmpty($scope.submitData.model_name)){
            $scope.switchForm.model_name.$setValidity("error", false);
        } else {
            $scope.switchForm.model_name.$setValidity("error", true);
        }

        if(this.isObjectEmpty($scope.submitData.model_data.tier_roles)){
            $scope.switchForm.tier_roles.$setValidity("error", false);
        } else {
            $scope.switchForm.tier_roles.$setValidity("error", true);
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

    $scope.getLinecardList = function() {
        var abc = angular.copy(appSettings.appAPI.linecard.list);
        abc.url = abc.url+"?type=linecards";
        appServices.doAPIRequest(appSettings.appAPI.linecard.list, null, null).then(function(data) {
            $scope.linecards = data;
            console.log(JSON.stringify(data));
            $scope.module_list = [{
                "name" : "--Select--",
                "id" : "0"
            }];
            /*$scope.lc_list = [{
                "name" : "--Select--",
                "id" : "0"
            }];*/
            $scope.lc_list = [];
            for(var i=0; i<$scope.linecards.length; i++){
                if($scope.linecards[i].lc_type === 'Linecard'){
                    $scope.lc_list.push($scope.linecards[i]);
                } else {
                    $scope.module_list.push($scope.linecards[i]);
                }
            }
            if(!$scope.isObjectEmpty($scope.lc_list) && !$scope.isObjectEmpty($scope.submitData.switch_data.slots) && $scope.isObjectEmpty($scope.submitData.switch_data.slots[0].lc_id)){
                $scope.submitData.switch_data.slots[0].lc_id = $scope.lc_list[0].id;
            }
        });
    };

    $scope.getData = function(){
        this.getLinecardList();
       if($scope.action ==  'view' || $scope.action == 'edit') {
            var getDataById = angular.copy(appSettings.appAPI.switches.getById);
            getDataById.url = getDataById.url+dataToModal.id;
            appServices.doAPIRequest(getDataById, null, null).then(function(data) {
                $scope.submitData = data;
                console.log(JSON.stringify(data)+" ************************************************** ********");
                if(0 === $scope.submitData.switch_data.module_id && 'edit' === $scope.action){
                    $scope.submitData.switch_data.module_id = "0";
                }
            });
        }
    };

    $scope.init = function() {
        $scope.getData();
    };

    $scope.changeAction = function(newAction) {
        $scope.action = newAction;
        if(0 === $scope.submitData.switch_data.module_id && 'edit' === newAction){
            $scope.submitData.switch_data.module_id = "0";
        }
    };

    $scope.deleteSwitch = function() {
        dataToModal.callerScope.deleteSwitch(dataToModal.id, dataToModal.index);
    };

    $scope.init();
});

angular.module('PoapServer').controller('SwitchStatusModalCtrl', 
    function($scope, $modalInstance, appSettings, appServices, dataToModal, $filter, ngTableParams) {
    $scope.appServices = appServices;
        $scope.switches = [];
        $scope.id = dataToModal.id;
        $scope.status = dataToModal.status;

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

        $scope.toggleAnimation = function() {
            $scope.animationsEnabled = !$scope.animationsEnabled;
        };

        $scope.$watch("searchKeyword", function () {
            $scope.tableParams.reload();
            $scope.tableParams.page(1);
        });
        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.init = function() {
            var reqHeader = {
                appendToURL : true,
                value : $scope.id+'/status/'+$scope.status,
                noTrailingSlash : true
            };
            appServices.doAPIRequest(appSettings.appAPI.switches.switch_modal_status, null, reqHeader).then(function(data) {
               $scope.switches = data;
               $scope.tableParams.reload();
            });
        };

        $scope.init();
});