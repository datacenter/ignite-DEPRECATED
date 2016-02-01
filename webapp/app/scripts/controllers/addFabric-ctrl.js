'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('AddFabricInstanceCtrl', function($scope, $routeParams, $http, $location, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService, ngToast) {
    /* When we enter tha app we need to remove the background from the login page and include headers and footers*/
    appServices.setInternalAppUI($scope)

    var parent = $scope.$parent;

    $scope.images = null;

    // Local constants
    $scope.choices = [{'id' : 1, 'value': 'YES'},
                     {'id' : 0, 'value': 'NO'}];
    // Local constants :: Ends Here

    /**Modal**/

    $scope.topologyData = "";

    $scope.animationsEnabled = true;

    $scope.fabricData = {
        "name": "",
        "submit": "false",
        "instance": appSettings.defaultData.fabricInstance.replica,
        "topology_id": appSettings.defaultData.fabricInstance.topologyId,
        "locked": appSettings.defaultData.fabricInstance.locked,
        "validate": appSettings.defaultData.fabricInstance.validate,
        //"config_json": [],
        "system_id" : []
    };


    /*
        "image_details" : {
          "leaf_switch" : "",
          "spine_switch" : "",
        }
    */


    $scope.getImages = function() {
      appServices.doAPIRequest(appSettings.appAPI.images.list, null, null).then(function(data) {
          $scope.images = data;
      });
    };


    $scope.getFabricProfiles = function() {
      appServices.doAPIRequest(appSettings.appAPI.fabricProfile.list, null, null).then(function(data) {
          $scope.fabricProfiles = data;
      });
    };



    $scope.setConfigModal = function(size) {
      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/setConfigurationModal.html',
        controller: 'SetConfigModalCtrl',
        size: size,
        backdrop: 'static',
        resolve: {
          dataToModal: function() {
            return {
              configurations : $scope.configurations,
              fabricData : $scope.fabricData,
              action : $scope.action,
              images : $scope.images,
              fabricProfiles : $scope.fabricProfiles,
              switchList : $scope.switchList
            }
          }
        }
      });

      modalInstance.result.then(function(modalData) {
        angular.extend($scope.fabricData, modalData.submitData);
        $log.debug('Modal Closed with Apply.');
        $log.debug(modalData.submitData);
        $log.debug($scope.fabricData);
      }, function() {
        $log.info('Modal dismissed at: ' + new Date());
      });

    };

    $scope.getSwitchNames = function() {
        var switchList = [];
        var data = $scope.topologyData;
        var switchList = [];
        $scope.topologyData.topology_json.core_list.map(function(data) { switchList.push(data.name); });
        $scope.topologyData.topology_json.spine_list.map(function(data) { switchList.push(data.name); });
        $scope.topologyData.topology_json.leaf_list.map(function(data) { switchList.push(data.name); });
        
        return switchList;
    };


    $scope.setSerialIDModal = function(size) {
      var switchNames = $scope.getSwitchNames();
      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/setSerialIDModal.html',
        controller: 'SetSerialIDModalCtrl',
        size: size,
        backdrop: 'static',
        resolve: {
          dataToModal: function() {
            return {
              switchNames : switchNames,
              fabricName : $scope.fabricData.name,
              system_id : $scope.fabricData.system_id,
              replicas : $scope.fabricData.instance,
              action : $scope.action
            };
          }
        }
      });

      modalInstance.result.then(function(modalData) {
          $scope.fabricData.system_id = modalData.submitData;
      }, function() {
        $log.info('Modal dismissed at: ' + new Date());
      });

    };

    $scope.bluidConfig = function() {
      
      var dataToSubmit = $scope.fabricData;
      var fabridId = $scope.fabricData.id
      var requestHeader = {
        appendToURL: true,
        value: fabridId +'/buildconfig',
        noTrailingSlash: false
      };
      appServices.doAPIRequest(appSettings.appAPI.fabricInstance.buildConfig, dataToSubmit, requestHeader).then(function(data) {
        ngToast.create({
            className: 'success',
            content: data
          });
      });
    };

    $scope.getTopologyData = function(topologyId) {
      $scope.submitData.config_json = [];
      $scope.topologyData = "";
      
      var requestHeader = {
        appendToURL: true,
        value: topologyId,
        noTrailingSlash: true
      };

      appServices.doAPIRequest(appSettings.appAPI.topology.getById, null, requestHeader).then(function(data) {
        $log.debug('Data Fetched for Topology Id : ' + topologyId);
        $log.debug(data);
        $scope.topology = angular.copy(data);
        $log.debug($scope.topology);
        var switchList = [];
        $log.debug($scope.topology.topology_json.spine_list);
        $scope.topology.topology_json.spine_list.map(function(spine) { switchList.push(spine.name); });
        $log.debug($scope.topology.topology_json.leaf_list);
        $scope.topology.topology_json.leaf_list.map(function(leaf) { switchList.push(leaf.name); });
        $log.debug(switchList);
          
        /*angular.forEach(switchList, function(switchName) {
          $scope.fabricData.config_json.push({'name': switchName, 'configuration_id' : appSettings.defaultData.fabricInstance.buildConfigurationId});
        });*/

        $scope.switchList = switchList;
        $log.debug($scope.submitData);
        $scope.topologyData = data;
        // setTopologyData($scope.topology);
        $log.debug('Topolgy Loaded.');
      });
    }

    $scope.addFabricInstanceModal = function(size) {

      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/addFabricInstanceModal.html',
        controller: 'AddFabricInstanceModalCtrl',
        size: size
      });

      modalInstance.result.then(function(selectedItem) {
        $scope.selected = selectedItem;
      }, function() {
        $log.info('Modal dismissed at: ' + new Date());
      });

    };

    $scope.toggleAnimation = function() {
      $scope.animationsEnabled = !$scope.animationsEnabled;
    };

    /**Modal**/
    $scope.goBack = function(path) {
      $location.path(path);
    };
    
    $scope.goBackToList = function() {
      this.goBack('/fabricInstance');
    };

    $scope.getTopologyList = function() {
      appServices.doAPIRequest(appSettings.appAPI.topology.list, null, null).then(function(data) {
        $scope.topologies = angular.copy(data);
      });
    };

    $scope.getConfigurationList = function() {
      appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, null).then(function(data) {
        $scope.configurations = angular.copy(data);
      });
    };

    $scope.changeAction = function(newAction) {
      $scope.action = newAction;
    }

    $scope.deleteFabricInstance = function(id) {
      $scope.selectedId = id;

      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/deleteModal.html',
        controller: 'FabricInstanceDeleteModalCtrl',
        size: 'md',
        backdrop: 'static',
        resolve: {
          dataToModal: function() {
            return {
              id: $scope.selectedId,
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
    }

    $scope.cloneFabricInstance = function(id) {
      $log.debug('Cloning Fabric Instance ID : ' + id);
      $scope.action = "clone";
      $scope.selectedId = id;
      $scope.openCloneModal();
    }

    $scope.openCloneModal = function(size) {
      $log.debug('Executing Clone Modal.');
      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/cloneModal.html',
        controller: 'FabricInstanceCloneModalCtrl',
        size: 'sm',
        backdrop: 'static',
        resolve: {
          dataToModal: function() {
            return {
              action: $scope.action,
              id: $scope.selectedId
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

    $scope.submitData = function(modalData) {
      if (modalData.action == 'delete') {

        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId,
          noTrailingSlash: true
        };

        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.delete, null, reqHeader).then(function(data) {
          ngToast.create({
            className: 'success',
            content: 'Fabric Instance Deleted Successfully.'
          });
          $scope.goBack('/fabricInstance');
        });
      } else if (modalData.action == 'clone') {
        debugger;
        var dataToSubmit = modalData.submitData;
        var requestHeader = {
          appendToURL: true,
          value: $scope.selectedId,
          noTrailingSlash: true
        };
        $log.debug('Request Header');
        $log.debug(requestHeader);
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.getById, null, requestHeader).then(function(data) {
          $log.debug('Data Fetched for Fabric Instance Id : ' + $scope.selectedId);
          $log.debug(data);
          var newFabricInstance = angular.copy(data);
          newFabricInstance.id = "";
          newFabricInstance.name = modalData.submitData.NewCloneName;
          newFabricInstance.submit = "false";
          newFabricInstance.topology_id = newFabricInstance.topology.topology_id;

          newFabricInstance.image_details.switch_image_profile=[];
          newFabricInstance.system_id = [];
          newFabricInstance.config_json.switch_config_id=[];

          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.add, newFabricInstance, null).then(function(data) {
            $log.debug('Fabric Instance Cloned.');
            $log.debug(data);
            ngToast.create({
              className: 'success',
              content: 'Fabric Instance Cloned Successfully.'
            });
            $scope.goBack('/fabricInstance/edit/' + data.id);
          });
        });
      }
    }

    $scope.submitFabricInstance = function() {
      $log.debug('Submitting Fabric Instance.');
      var dataToSubmit = $scope.fabricData;
      console.log(dataToSubmit);
      dataToSubmit.submit = true;
      if ($scope.action == "add") {
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.add, dataToSubmit, null).then(function(data) {
          $log.debug('Fabric Instance Submitted.');
          ngToast.create({
            className: 'success',
            content: 'Fabric Instance Submitted Successfully.'
          });
          $scope.goBack('/fabricInstance');
        });
      } else if ($scope.action == "edit") {
        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId,
          noTrailingSlash:true
        };
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, dataToSubmit, reqHeader).then(function(data) {
          $log.debug('Fabric Instance Submitted.');
          ngToast.create({
            className: 'success',
            content: 'Fabric Instance Submitted Successfully.'
          });
          $scope.goBack('/fabricInstance');
        });
      }
    }

    $scope.saveFabricInstance = function() {
      var dataToSubmit = $scope.fabricData;

      if ($scope.action == "add") {
        $log.debug('Adding new Fabric Instance to DB.');
        console.log(dataToSubmit);
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.add, dataToSubmit, null).then(function(data) {
          $log.debug('Fabric Instance Added.');
          ngToast.create({
            className: 'success',
            content: 'Fabric Instance Created Successfully.'
          });
          $scope.goBack('/fabricInstance/edit/' + data.id);
        });
      } else if ($scope.action == "edit") {
        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId,
          noTrailingSlash: true
        };$log.debug('DATA FOR PUT Request.');$log.debug(dataToSubmit);
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, dataToSubmit, reqHeader).then(function(data) {
          $log.debug('Fabric Instance Updated.');
          $log.debug(data);
          ngToast.create({
            className: 'success',
            content: 'Fabric Instance Updated Successfully.'
          });
          $scope.goBack('/fabricInstance/edit/' + data.id);
        });
      }
    }

    $scope.loadFabricInstance = function(fabricInstanceId) {
      var requestHeader = {
        appendToURL: true,
        value: fabricInstanceId,
        noTrailingSlash: true
      };
      appServices.doAPIRequest(appSettings.appAPI.fabricInstance.getById, null, requestHeader).then(function(data) {
        $log.debug('Data Fetched for Fabric Instance Id : ' + $scope.selectedId);
        $log.debug(data);
        $scope.fabricData.id = angular.copy(data.id);
        $scope.fabricData.name = angular.copy(data.name);
        $scope.fabricData.submit = angular.copy(data.submit);
        $scope.fabricData.instance = angular.copy(data.instance);
        $scope.fabricData.topology_id = angular.copy(data.topology.topology_id);
        $scope.fabricData.locked = angular.copy(data.locked);
        $scope.fabricData.validate = angular.copy(data.validate);
        $scope.fabricData.config_json = angular.copy(data.config_json);
        $scope.fabricData.profiles = angular.copy(data.profiles);
        $scope.fabricData.image_details = angular.copy(data.image_details);
        $scope.fabricData.system_id = angular.copy(data.system_id);
        $scope.topologyData = angular.copy(data.topology);


        $scope.getTopologyData($scope.fabricData.topology_id);

        /*if(typeof data.image_details.leaf_switch != 'undefined') {
            $scope.fabricData.image_details.leaf_switch = data.image_details.leaf_switch;
            $scope.fabricData.image_details.spine_switch = data.image_details.spine_switch;  
        }*/
        
        $log.debug('Collected Fabric Data After GET');
        $log.debug($scope.fabricData);
      });
    }

    $scope.processRequest = function() {
      if ($scope.action == 'add') {

      } else if ($scope.action == 'edit' || $scope.action == 'view') {
        // Load Actual Topology Data
        $log.debug('Its a Edit or View Request.');
        $log.debug('For ID : ' + $scope.selectedId)
        $scope.loadFabricInstance($scope.selectedId);
      }
    }

    $scope.init = function() {
      $scope.selectedId = $routeParams.fabricInstanceId;
      $scope.action = $routeParams.mode;
      $scope.getConfigurationList();
      $scope.getTopologyList();
      $scope.processRequest();
      $scope.getImages();
      $scope.getFabricProfiles();

    };

    angular.element('#topology_svg').ready(function() {
      $log.debug(angular.element('#topology_svg'));
      $log.debug('Document Loaded');
      $scope.init();
    });
  });

angular.module('PoapServer').controller('AddFabricInstanceModalCtrl', function($scope, $modalInstance) {

  $scope.ok = function() {
    $modalInstance.close();
  };
  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };
});

angular.module('PoapServer').controller('SetConfigModalCtrl', function($scope, $modalInstance, $log, appSettings, appServices, dataToModal) {

  $scope.switchDetails = false;
  $scope.appSettings = appSettings;
  $scope.fabricProfiles = dataToModal.fabricProfiles;
  $scope.configurations = dataToModal.configurations;
  $scope.images = dataToModal.images;
  $scope.switchList = dataToModal.switchList;

  /*$scope.submitData.image_details.spine_image_profile = -1;
  $scope.submitData.image_details.leaf_image_profile = -1;*/

  $scope.fabricData = dataToModal.fabricData;
  
  $scope.action = dataToModal.action;
  
  $scope.toggleSwitch = function() {
    if($scope.switchDetails == true) {
      $scope.switchDetails = false;
    }
    else {
      $scope.switchDetails = true; 
    }
  };

  $scope.tempConfigurations = [];
  $scope.tempConfigObject = {
    "switch_name" : "",
    "profile_id" : "",
    "configuration_id" : "",
    "image_profile" : ""
  };

  $scope.submitData = {
        "image_details" : {
          "leaf_image_profile": "",
          "spine_image_profile": "",
          "switch_image_profile": []
        },
        "config_json": {
          "leaf_config_id": "",
          "spine_config_id": "",
          "switch_config_id": []
        },
        "profiles" : {
          "leaf_profile_id": "",
          "spine_profile_id": "",
          "switch_profile_id": []
        }
  }; 

  $scope.addAnother = function() {
    var configObj = angular.copy($scope.tempConfigObject)
    $scope.tempConfigurations.push(configObj);
  };

  $scope.generateSubmitData = function() {
      angular.forEach($scope.tempConfigurations, function(val, key) {
          var configObj = {
            "name" : val.switch_name,
            "configuration_id" : Number(val.configuration_id)
          };

          if(val.image_profile === ''){
            val.image_details = -1;
          }

          var imageObj = {
            "name" : val.switch_name,
            "image_profile" : val.image_profile
          };

          var profileObj = {
            "name" : val.switch_name,
            "profile_id" : Number(val.profile_id)
          };

          $scope.submitData.image_details.switch_image_profile.push(imageObj) 
          $scope.submitData.config_json.switch_config_id.push(configObj) 
          $scope.submitData.profiles.switch_profile_id.push(profileObj) 

      });
  };

  $scope.deleteConfig = function(index) {
      $scope.tempConfigurations.splice(index, 1);
  };

  $scope.ok = function() {
    $log.debug('Closing Modal..');
    $log.debug($scope.submitData);

    $scope.generateSubmitData();

    if(typeof $scope.submitData.config_json.leaf_config_id != 'undefined'){
      $scope.submitData.config_json.leaf_config_id = Number($scope.submitData.config_json.leaf_config_id);
    }
    
    if(typeof $scope.submitData.config_json.spine_config_id != 'undefined'){
      $scope.submitData.config_json.spine_config_id = Number($scope.submitData.config_json.spine_config_id);
    }
    
    if(typeof $scope.submitData.profiles.leaf_profile_id != 'undefined'){
      $scope.submitData.profiles.leaf_profile_id = Number($scope.submitData.profiles.leaf_profile_id);
    }
    
    if(typeof $scope.submitData.profiles.spine_profile_id != 'undefined'){
      $scope.submitData.profiles.spine_profile_id = Number($scope.submitData.profiles.spine_profile_id);
    }

    if($scope.submitData.image_details.leaf_image_profile === ''){
      $scope.submitData.image_details.leaf_image_profile = -1;
    }

    if($scope.submitData.image_details.spine_image_profile === ''){
      $scope.submitData.image_details.spine_image_profile = -1;
    }

    $modalInstance.close({
      submitData : $scope.submitData,
      action : $scope.action
    });
  };

  $scope.setEditData = function() {
        if(typeof $scope.fabricData.image_details != 'undefined') {
          $scope.submitData.image_details.leaf_image_profile = $scope.fabricData.image_details.leaf_image_profile;
          $scope.submitData.image_details.spine_image_profile = $scope.fabricData.image_details.spine_image_profile;  
        }
        
        
        if(typeof $scope.fabricData.config_json != 'undefined') {
          $scope.submitData.config_json.leaf_config_id = $scope.fabricData.config_json.leaf_config_id.toString();
          $scope.submitData.config_json.spine_config_id = $scope.fabricData.config_json.spine_config_id.toString();
        }

        if(typeof $scope.fabricData.profiles != 'undefined') {
          $scope.submitData.profiles.leaf_profile_id = $scope.fabricData.profiles.leaf_profile_id.toString();
          $scope.submitData.profiles.spine_profile_id = $scope.fabricData.profiles.spine_profile_id.toString();
        }

        if(typeof $scope.fabricData.config_json != 'undefined'){
          if($scope.fabricData.config_json.switch_config_id.length > 0) {
              //$scope.switchDetails = true;
              angular.forEach($scope.fabricData.config_json.switch_config_id, function(val, key) {
                var tempConfigObject =  {
                    "switch_name" : val.name,
                    "profile_id" : $scope.fabricData.profiles.switch_profile_id[key].profile_id.toString(),
                    "configuration_id" : val.configuration_id.toString(),
                    "image_profile" : $scope.fabricData.image_details.switch_image_profile[key].image_profile
                };
                $scope.tempConfigurations.push(tempConfigObject);
              })
          }
        }
  };   


  



  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.init = function() {
    $scope.setEditData();
  };

  $scope.init();
});


angular.module('PoapServer').controller('SetSerialIDModalCtrl', function($scope, $modalInstance, $log, appSettings, appServices, dataToModal) {
    var dataModel = {"name":"","system_id":""};
    $scope.serialIDs = dataToModal.system_id;
    $scope.fabricName = dataToModal.fabricName;
    $scope.switchNames = []; 
    $scope.replicas = dataToModal.replicas;
    $scope.action = dataToModal.action;

    $scope.setSwitchNames = function() {
        angular.forEach(dataToModal.switchNames, function(v, k) {
            for(var i = 1; i <= $scope.replicas; i++) {
                var switchName = $scope.fabricName + '_' + i + '_' + v;
                $scope.switchNames.push(switchName);
            }
        });
    };

    $scope.deleteSerialID = function(index) {
      $scope.serialIDs.splice(index, 1);
    };

    $scope.addAnotherSwitchID = function() {
      $scope.serialIDs.push(angular.copy(dataModel)); 
    };

    $scope.ok = function() {
      $modalInstance.close({
        submitData: $scope.serialIDs
      });
    };

    $scope.cancel = function() {
      $modalInstance.dismiss('cancel');
    };

    $scope.setSwitchNames();

});


angular.module('PoapServer').controller('FabricInstanceCloneModalCtrl', function($scope, $modalInstance, appSettings, appServices, dataToModal) {

  $scope.action = dataToModal.action;
  $scope.id = dataToModal.id;
  $scope.submitData = {
    "NewTopologyName": ""
  }

  $scope.ok = function() {
    $modalInstance.close({
      submitData: $scope.submitData,
      action: $scope.action,
      id: $scope.id
    });
  };

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

});

angular.module('PoapServer').controller('FabricInstanceDeleteModalCtrl',
  function($scope, $modalInstance, appSettings, appServices, dataToModal) {

    $scope.ok = function() {
      $modalInstance.close({
        action: 'delete',
        id: dataToModal.id
      });
    };

    $scope.cancel = function() {
      $modalInstance.dismiss('cancel');
    };

  });
