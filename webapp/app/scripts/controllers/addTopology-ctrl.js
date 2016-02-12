'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:DashboardCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
  .controller('AddTopologyCtrl', function($scope, $rootScope, $routeParams, $http, $location, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, $timeout, roundProgressService, ngToast) {
    var parent = $scope.$parent;
    $scope.goBack = function(path) {
        $location.path(path);
      }
      /**Popover**/
    $scope.dynamicPopover = {
      templateUrl: 'topologyPopoverDir.html'
    };
    $scope.topologyPopover = {
      templateUrl: 'topologyPopFormDir.html'
    };
    $scope.topologyDisplayPopover = {
      templateUrl: 'topologyDisplayPopover.html',

    };

    $scope.editSwitch = function() {
      $scope.editSwitchFlag = true;
    };

    $scope.editLink = function() {
      $scope.editLinkFlag = true;
    };

    $scope.editName = function() {
      $scope.nameEdit = true;
    };

    $scope.closeSwitchEdit = function() {
      $scope.editSwitchFlag = false;
      $scope.topologyData = angular.copy($scope.topology);
    };

    $scope.closeLinkEdit = function() {
      $scope.editLinkFlag = false;
      $scope.topologyData = angular.copy($scope.topology);
    };

    $scope.cancelNameEdit = function() {
      $scope.nameEdit = false;
      $scope.topologyData = angular.copy($scope.topology);
    };

    $scope.cancelDelete = function() {
      $scope.editLinkFlag = false;
      $scope.editSwitchFlag = false;
      $scope.topologyData = angular.copy($scope.topology);
    };

    $scope.saveName = function() {
      $scope.nameEdit = false;
      //$scope.topologyData = angular.copy($scope.topology);
      var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId,
          noTrailingSlash: true
        };

      var editNameRequest = appSettings.appAPI.topology.edit;

      $scope.submitName = {
        "name" : $scope.topologyData.name
      };

      if('fabric' == $scope.source) {
        editNameRequest = appSettings.appAPI.fabricInstance.edit;
      }
        
      appServices.doAPIRequest(editNameRequest, $scope.submitName, reqHeader).then(function(data) {
          /* TODO after delete success */
          if(!("" == data || null == data)) {
            $scope.topology = data;
            $scope.topologyData = angular.copy($scope.topology);
            $scope.viewAddedSwitches(data);
          } else {
            $scope.topology.name = $scope.topologyData.name;
          }
          ngToast.create({
            className: 'success',
            content: 'Name updated, successfully!.'
          });
        });
    };

    $scope.goBackToList = function() {
      var path = '/topology';
      if('fabric' == $scope.source) {
        path = '/fabricInstance';
      }
      this.goBack(path);
    };

    $scope.switchDetails = {
      'defaults_switch_name':[],
      'default_switches':[],
      'selectList':{},
      'count' : {
        'Core' : 0,
        'Spine': 0,
        'Leaf' : 0,
        'Border': 0,
      }
    };

    $scope.addLink = {};

    /**./Popover**/
    $scope.select = function(item) {
      $scope.selected = item;
    };
    $scope.isActive = function(item) {
      return $scope.selected === item;
    };

    /*********************************************************************************************************************/

    //NOT DONE
    $scope.notDone = function() {
      alert('Not Implemented');
    }

    $scope.getTierCount = function() {
      var switch_types = ['Core','Spine','Leaf','Border'];
      angular.forEach(switch_types, function(value,key){
        $scope.switchDetails.count[value] = $scope.topology.switches.filter(function(a){
          if(a.tier == value){
            return a;
          }
        }).length;
      });
    };

    $scope.viewAddedSwitches = function(data) {
      this.getLinkDetails();
      
      data.switches = data.switches.filter(function(a) {
          if(null == a.model) {
            a.type = $scope.switchDetails.defaults_switch_name[a.tier];
          } else {
            $scope.switchDetails.selectList.switch_list.filter(function(b) {
              if(a.model == b.id) {
                a.type = b.name;
              }
            });
          }
          return a;
      });
      $scope.topologyData = angular.copy($scope.topology);
      doReload(data);
    };

    /************************* Add Switch ***********************/

    $scope.addSwitch = function() {
      $scope.action = 'add_switch';
      $scope.openAddSwitchModal();
    };

    $scope.openAddSwitchModal = function() {
            $scope.modalInstance = $modal.open({
                animation: $scope.animationsEnabled,
                templateUrl: 'pages/template/modal/addTopoSwitchModal.html',
                controller: 'AddSwitchModalCtrl',
                size: 'sm',
                backdrop: 'static',
                resolve: {
                    dataToModal : function() {
                        return {
                            action : $scope.action,
                            id : $scope.selectedId,
                            source : $scope.source,
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

    /************************* Save Reload ***********************/

    $scope.saveLinkEdit = function(id, index) {
      $('#popEditLink_Item'+index).modal('toggle');

      var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId+"/link/"+id,
          noTrailingSlash: true
        };

      $scope.editLinkFlag = false;

      $scope.submitLinkData = {
        "link_type": $scope.topologyData.links[index].link_type,
        "num_links": $scope.topologyData.links[index].num_links,
        "src_ports": $scope.topologyData.links[index].src_ports,
        "dst_ports": $scope.topologyData.links[index].dst_ports
      };

      appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, $scope.submitLinkData, reqHeader).then(function(data) {
          /* TODO after delete success */
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.viewAddedSwitches(data);
        });
    
    };


    $scope.saveSwitchEdit = function(id, index) {

      $('#popEdit_Item_'+id).modal('toggle');

      var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId+"/switch/"+id,
          noTrailingSlash: true
        };

      var editRequest = appSettings.appAPI.topology.edit;

      $scope.editSwitchFlag = false;

      $scope.submitSwitchData = {
        "model" : $scope.topologyData.switches[index].model,
        "image_profile" : $scope.topologyData.switches[index].image_profile
      };

      if('fabric' == $scope.source) {
        $scope.submitSwitchData = {
            "model" : $scope.topologyData.switches[index].model,
            "image_profile" : $scope.topologyData.switches[index].image_profile,
            "name": $scope.topologyData.switches[index].name,
            "serial_num": $scope.topologyData.switches[index].serial_num,
            "config_profile": $scope.topologyData.switches[index].config_profile,
            "feature_profile": $scope.topologyData.switches[index].feature_profile,
            "workflow": $scope.topologyData.switches[index].workflow
        };

        editRequest = appSettings.appAPI.fabricInstance.edit;
      }
        
      appServices.doAPIRequest(editRequest, $scope.submitSwitchData, reqHeader).then(function(data) {
          /* TODO after delete success */
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.viewAddedSwitches(data);
        });
    };

    /**************** Modify *********************/

    $scope.modify = function() {
      var reqHeader = {
        appendToURL: true,
        value: $scope.selectedId+"/defaults",
        noTrailingSlash: true
      };
      var defaultsEditReq = appSettings.appAPI.topology.edit;
      if('fabric' == $scope.source) {
        defaultsEditReq = appSettings.appAPI.fabricInstance.edit;
      }
      appServices.doAPIRequest(defaultsEditReq, $scope.defaults, reqHeader).then(function(data) {
        $scope.topology = data;
        $scope.tierCounter = 0;
        $scope.getLinkDetails();
        $scope.getSwitchDetails('reloadTopology');
      });
    };

    /*********************** Delete Item ***********************/
    $scope.toDeleteItem = 0;
    $scope.itemType = "";

    $scope.deleteSwitch = function(id) {

      $('#popEdit_Item_'+id).modal('toggle');
      $('#modalDeleteContent').html('Are you sure you want to delete this switch?');
      $('#myModalDelete').modal('toggle');   
      $scope.toDeleteItem = id;
      $scope.itemType = 'switch';
    };

    $scope.removeItemLinkType = function(id, index) {

        $('#popEditLink_Item'+index).modal('toggle');
        $('#modalDeleteContent').html('Are you sure you want to delete this link?');
        $('#myModalDelete').modal('toggle');   
        $scope.toDeleteItem = id;
        $scope.itemType = 'link';
    };

    $scope.deleteItem = function() {
      var valToAppend = $scope.selectedId+"/"+$scope.itemType+"/"+$scope.toDeleteItem;
       var reqHeader = {
          appendToURL: true,
          value: valToAppend,
          noTrailingSlash: true
        };

        var deleteSwitchRequest = appSettings.appAPI.topology.delete;
        if($scope.source == 'fabric') {
          deleteSwitchRequest = appSettings.appAPI.fabricInstance.delete;
        }

        appServices.doAPIRequest(deleteSwitchRequest, null, reqHeader).then(function(data) {
          /* TODO after delete success */
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.getTierCount();
          $scope.viewAddedSwitches(data);
        });
    };

    /**************Add Link ******************************/

    $scope.addLinkModal = function(linkFor) {
      $scope.linkFor = linkFor;
      $scope.topologyData.src_switch = [];
      $scope.topologyData.dst_switch = [];
      $scope.topologyData.linkType = [];

      $scope.addLink.num_links = 1;
      $scope.addLink.link_type = null;
      
      if('core2spine' === linkFor) {
        $scope.topologyData.src_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Core'});
        $scope.topologyData.dst_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Spine'});
        $scope.topologyData.linkType = [
              {'name':'PHYSICAL','id':'Physical'},
              {'name':'PORT_CHANNEL', 'id':'Port-Channel'}
            ];
      } else if('spine2leaf' === linkFor) {
        $scope.topologyData.src_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Spine'});
        $scope.topologyData.dst_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Leaf'});
        $scope.topologyData.linkType = [
              {'name':'PHYSICAL','id':'Physical'},
              {'name':'PORT_CHANNEL', 'id':'Port-Channel'}
            ];
        $scope.addLink.num_links = $scope.topology.defaults.links[0].num_links;
        $scope.addLink.link_type = $scope.topology.defaults.links[0].link_type;
      } else if('leaf2border' === linkFor) {
        $scope.topologyData.src_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Leaf'});
        $scope.topologyData.dst_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Border'});
        $scope.topologyData.linkType = [
              {'name':'PHYSICAL','id':'Physical'},
              {'name':'PORT_CHANNEL', 'id':'Port-Channel'}
            ];
      } else if('leaf2leaf' === linkFor) {
        $scope.topologyData.src_switch = $scope.topologyData.dst_switch = $scope.topology.switches.filter(function(a) {return a.tier === 'Leaf'});
        $scope.topologyData.linkType = [
              {'name':'VPC_PEER','id':'VPC-Peer'},
              {'name':'VPC_MEMBER', 'id':'VPC-Member'}
            ]
      }
      if($scope.topologyData.linkType.length != 0 && $scope.addLink.link_type == null){
        $scope.addLink.link_type = $scope.topologyData.linkType[0].id;
      }
      $('#myModalLink').modal('toggle');
    }

    $scope.checkLinkExists = function(linkObj) {


      $log.debug('src_switch and dst_switch');
      var src_switch = linkObj.src_switch;
      var dst_switch = linkObj.dst_switch;
      var link_type = linkObj.link_type;
      console.log(linkObj.src_switch);
      console.log(linkObj.dst_switch);
      console.log(linkObj.link_type);

      if (src_switch != undefined && dst_switch != undefined && linkObj.link_type != undefined && linkObj.num_links > 0 && linkObj.num_links < 9) {

        if (src_switch == dst_switch) {
          $('#alertLinkSame').show()
        } else {
          $('#alertLinkSame').hide()
        }

        debugger;

        for (var i = 0; i < $scope.topology.links.length; i++) {

          if ((link_type != 'VPC-Member') && ((($scope.topology.links[i].link_type == link_type) || $scope.linkFor != 'leaf2leaf')  && ($scope.topology.links[i].src_switch == src_switch && $scope.topology.links[i].dst_switch == dst_switch) || ($scope.topology.links[i].src_switch == dst_switch && $scope.topology.links[i].dst_switch == src_switch))) {
            $('#alertLinkExists').show();
            return false;
          } else {
            $('#alertLinkExists').hide();
          }
        }
      } else {
        $('#alertLinkExists').hide();
        return false;
      }

      return true;
    };



    $scope.createLink = function(linkObj) {
     
      $('#myModalLink').modal('toggle');

        var valToAppend = $scope.selectedId+"/link";
        var reqHeader = {
          appendToURL: true,
          value: valToAppend,
          noTrailingSlash: true
        };

        var addLinkData = appSettings.appAPI.topology.add_switch_Link;
        if($scope.source == 'fabric') {
          addLinkData = appSettings.appAPI.fabricInstance.add_switch_Link;
        }

        appServices.doAPIRequest(addLinkData, linkObj, reqHeader).then(function(data) {
          /* TODO after delete success */
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.viewAddedSwitches(data);
        });
    }

    /************************* Remove Item Link by removing its type if both are leaf *********************/

    

    $scope.toggleDetailsModel = false;

    $scope.resizeSvgArea = function() {
      document.getElementById('topology_container').className = "col-sm-8";
    };

    $scope.resetSvgArea = function() {
      document.getElementById('topology_container').className = "col-sm-12";
    };

    $scope.showDefaults = function() {
      $scope.defaultEdit = false;
      $scope.openDefaultsModal();
    };

    $scope.showConfig = function() {
      $scope.configEdit = false;
      $scope.openConfigModal();
    };

    $scope.openConfigModal = function() {
      var action = $scope.action;
      if('edit' == action || 'add_switch' == action) {
        action = 'editConfig';
      }
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/addFabricModal.html',
            controller: 'FabricConfigCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        action : action,
                        configEdit : $scope.configEdit,
                        topology : $scope.topology,
                        source : $scope.source,
                        config_list : $scope.switchDetails.selectList.config_list,
                        fabricProfile_list : $scope.switchDetails.selectList.fabricProfile_list,
                        workflow_list : $scope.switchDetails.selectList.workflow_list,
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

    $scope.openDefaultsModal = function() {
      var action = $scope.action;
      if('edit' == action || 'add_switch' == action) {
        action = 'editDefault';
      }
      if('fabric' == $scope.source) {
        $scope.modalContent = "Changes will be applied only to newly added switches & links. Are you sure you want to continue?";  
      }
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/createTopologyModal.html',
            controller: 'TopologyDefaultCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        action : action,
                        defaultEdit : $scope.defaultEdit,
                        topology : $scope.topology,
                        source : $scope.source,
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

    $scope.toggleDetails = function() {
      $scope.toggleDetailsModel = !$scope.toggleDetailsModel;
      if ($scope.toggleDetailsModel) {
        $scope.resizeSvgArea();
      } else {
        $scope.resetSvgArea();
      }
      this.viewAddedSwitches($scope.topology);
    };

    $scope.openDepSwitchConfigModal = function(statId) {
      $scope.modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/fabricConfigView.html',
        controller: 'DeployedSwitchConfigModalCtrl',
        size: 'lg',
        backdrop: 'static',
        resolve: {
            dataToModal : function() {
                return {
                    "statId" : statId
                }
            }
         }
      });
      $scope.modalInstance.result.then(function(modalData) {
         $log.info('Modal dismissed at: ' + new Date());
      }, function() {
          $log.info('Modal dismissed at: ' + new Date());
      });
    };

    $scope.openDepSwitchLogModal = function(statId) {
      $scope.modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/logs.html',
        controller: 'ViewFabricLogModalCtrl',
        size: 'lg',
        backdrop: 'static',
        resolve: {
            dataToModal : function() {
                return {
                    "statId" : statId
                }
            }
         }
      });
      $scope.modalInstance.result.then(function(modalData) {
         $log.info('Modal dismissed at: ' + new Date());
      }, function() {
          $log.info('Modal dismissed at: ' + new Date());
      });
    };

    $scope.PopEdit = function(id) {
      PopEdit(id);
    };

    $scope.PopEditLink = function(id) {
      PopEditLink(id);
    };

    /*********************************************************************************************************************/

    /*Initialize the topology*/
    $scope.init = function() {
      $log.debug('Initial Topology Object by creating a copy of the data got from JSON');
      $log.debug($scope.topology);
      $scope.action = $routeParams.mode;
      $scope.processRequest();
    }

    $scope.fetchTierSwitches = function(tier) {
          var reqHeader = {
                appendToURL : true,
                value : "?tier="+tier,
                noTrailingSlash : true
            };

            if(null == tier) {
              reqHeader = null;
            }
          
          appServices.doAPIRequest(appSettings.appAPI.switches.list, null, reqHeader).then(function(data) {
            if(null == tier) {
              $scope.switchDetails.selectList.switch_list = data;
            } else {
              $scope.switchDetails.selectList[tier] = data;
            }
          });
        };

    $scope.fetchFabricConf = function() {
      
      var reqHeader = {
          appendToURL: true,
          value: '?submit=true',
          noTrailingSlash: true
        };

      appServices.doAPIRequest(appSettings.appAPI.configuration.list, null, reqHeader).then(function(data) {
        $scope.switchDetails.selectList.config_list = data;
      });
      appServices.doAPIRequest(appSettings.appAPI.fabricProfile.list, null, reqHeader).then(function(data) {
        $scope.switchDetails.selectList.fabricProfile_list = data;
      });
      appServices.doAPIRequest(appSettings.appAPI.workflow.list, null, reqHeader).then(function(data) {
        $scope.switchDetails.selectList.workflow_list = data;
      });
    };
    $scope.processRequest = function() {
      $scope.switchDetails.selectList.linkType = [
              {'name':'PHYSICAL','id':'Physical'},
              {'name':'PORT_CHANNEL', 'id':'Port-Channel'},
              {'name':'VPC_PEER','id':'VPC-Peer'},
              {'name':'VPC_MEMBER', 'id':'VPC-Member'}
            ];
      this.fetchImageList();
      var fetchDetails = {};
        $scope.fetchTierSwitches(null);
        // Load Actual Topology Data

        $scope.editSwitchFlag = false;
        $scope.editLinkFlag = false;
        $scope.nameEdit = false;
        $scope.selectedId = $routeParams.topologyId;
        if($routeParams.fabricInstanceId != undefined){
          $scope.selectedId = $routeParams.fabricInstanceId;
          fetchDetails = appSettings.appAPI.fabricInstance.getById;
          $scope.source = 'fabric';
          $scope.fetchFabricConf();
        } else {
          $scope.selectedId = $routeParams.topologyId;
          fetchDetails = appSettings.appAPI.topology.getById;
          $scope.source = 'topology';
          $scope.editLinkFlag = true;
        }
        $log.debug('Its an Edit or View Request.');
        $scope.loadTopologyData(fetchDetails);
    };

    $scope.getSwitchDetails = function(command) {
      if(null == $scope.topology.config_profile) {
        $scope.topology.config_profile = 0;
      }
      if(null == $scope.topology.feature_profile) {
        $scope.topology.feature_profile = 0;
      }
      angular.forEach($scope.topology.defaults.switches, function(value,key){
        $scope.fetchTierSwitches(value.tier);
        if(null == value.config_profile) {
          value.config_profile = 0;
        }
        if(null == value.feature_profile) {
          value.feature_profile = 0;
        }
        if(null == value.workflow) {
          value.workflow = 0;
        }
        var getDataById = angular.copy(appSettings.appAPI.switches.getById);
            getDataById.url = getDataById.url+value.model;
            appServices.doAPIRequest(getDataById, null, null).then(function(data) {
                $scope.switchDetails.defaults_switch_name[value.tier] = data.name;
                $scope.switchDetails.default_switches.push(data);
                $scope.tierCounter++;
                if (command != undefined && $scope.tierCounter === $scope.topology.defaults.switches.length) {
                  $scope.topology.switches = $scope.topology.switches.filter(function(a) {
                      if(null == a.model) {
                        a.type = $scope.switchDetails.defaults_switch_name[a.tier];
                      } else {
                        $scope.switchDetails.selectList.switch_list.filter(function(b) {
                          if(a.model == b.id) {
                            a.type = b.name;
                          }
                        });
                      }
                      return a;
                  });
                  $scope.topologyData = angular.copy($scope.topology);
                  if('reloadTopology' == command) {
                    doReload($scope.topology);
                  } else if('loadTopology' == command) {
                    setTopologyData($scope.topology);
                  }
                }
            });
      });
    };

    $scope.loadTopologyData = function(fetchDetails) {
      var requestHeader = {
        appendToURL: true,
        value: $scope.selectedId,
        noTrailingSlash: true
      };
      
      appServices.doAPIRequest(fetchDetails, null, requestHeader).then(function(data) {
        $log.debug('Data Fetched for Topology Id : ' + $scope.selectedId);
        $scope.topology = angular.copy(data);
        $scope.tierCounter = 0;
        $scope.getLinkDetails();
        $scope.getSwitchDetails('loadTopology');
        $scope.getTierCount();
        $log.debug($scope.topology);
        $scope.topologyData = angular.copy($scope.topology);
        $log.debug($scope.topology);
        $log.debug('Topolgy Loaded.');
      });
    };

    $scope.getLinkDetails = function() {
      angular.forEach($scope.topology.links, function(value,key){
        var src_switch = $scope.topology.switches.filter(function(a) {
          if(a.id == value.src_switch) {
            return a;
          }
        });
        var dst_switch = $scope.topology.switches.filter(function(a) {
          if(a.id == value.dst_switch) {
            return a;
          }
        });

        value.src_switch_name = src_switch[0].name;
        value.dst_switch_name = dst_switch[0].name;
      });
    };

    $scope.submitWork = function() {
      if('topology' == $scope.source) {
        var msg = 'Are you sure you want to submit this topology?';
        this.alertOnAction($scope.selectedId, 'submit', msg);
      } else {
        var msg = 'Are you sure you want to submit this fabric?';
        this.alertOnAction($scope.selectedId, 'submit', msg);
      }
    };

    $scope.clearTopology = function() {
      var msg = 'Are you sure you want to clear the topology?';
      this.alertOnAction($scope.selectedId, 'clear', msg);
    };

    $scope.changeAction = function(newAction) {
      $scope.action = newAction;
    };

    $scope.deleteTopology = function(id) {
      $scope.selectedId = id;
      var message = 'Are you sure you want to delete?'
      this.alertOnAction(id,'delete',message);
    };

    $scope.buildConfig = function() {
      var reqHeader = {
        appendToURL: true,
        value: $scope.selectedId+"/build",
        noTrailingSlash: true
      };
      appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, null, reqHeader).then(function(data) {
       ngToast.create({
          className: 'success',
          content: 'Config built, successfully!.'
        });
        $scope.topology = data;
        $scope.topologyData = angular.copy($scope.topology);
        $scope.viewAddedSwitches(data);
      });
    };

    $scope.alertOnAction = function(id, action, msg) {

      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/deleteModal.html',
        controller: 'AlertModalCtrl',
        size: 'md',
        backdrop: 'static',
        resolve: {
          dataToModal: function() {
            return {
              id: $scope.selectedId,
              action: action,
              message: msg,
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

    $scope.fetchImageList = function() {
      var reqHeader = {
                appendToURL : true,
                value : '?state=true',
                noTrailingSlash : true
            };
      appServices.doAPIRequest(appSettings.appAPI.images.list, null, reqHeader).then(function(data) {
        $scope.switchDetails.selectList.imglist = data;
      });
    };

    $scope.submitData = function(modalData) {
      if(modalData.action === 'add_switch') {
        var valToAppend = $scope.selectedId+"/switch";
        var reqHeader = {
          appendToURL: true,
          value: valToAppend,
          noTrailingSlash: true
        };

        var addSwitchData = appSettings.appAPI.topology.add_switch_Link;
        if($scope.source == 'fabric') {
          addSwitchData = appSettings.appAPI.fabricInstance.add_switch_Link;
        }

        appServices.doAPIRequest(addSwitchData, modalData.submitData, reqHeader).then(function(data) {
          /* TODO after delete success */
          /*$scope.goBack('/topology');*/
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.getTierCount();
          $scope.viewAddedSwitches(data);
        });
      } else if(modalData.action == 'editDefault') {
          $scope.defaults = modalData.submitData.defaults;
          if('topology' == $scope.source) {
            this.modify();
          }
      } /*else if (modalData.action == 'editDefault') {
        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId+"/defaults",
          noTrailingSlash: true
        };
        var defaultsEditReq = appSettings.appAPI.topology.edit;
        if('fabric' == $scope.source) {
          defaultsEditReq = appSettings.appAPI.fabricInstance.edit;
        }
        appServices.doAPIRequest(defaultsEditReq, modalData.submitData.defaults, reqHeader).then(function(data) {
          $scope.topology = data;
          $scope.tierCounter = 0;
          $scope.getLinkDetails();
          $scope.getSwitchDetails('reloadTopology');
        });
        
      } */else if (modalData.action == 'delete') {
        if('fabric' == $scope.source) {
          var reqHeader = {
            appendToURL: true,
            value: $scope.selectedId,
            noTrailingSlash: true
          };

          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.delete, null, reqHeader).then(function(data) {
            /* TODO after delete success */
            $scope.goBack('/fabricInstance');
          });
        } else {
          var reqHeader = {
            appendToURL: true,
            value: $scope.selectedId,
            noTrailingSlash: true
          };

          appServices.doAPIRequest(appSettings.appAPI.topology.delete, null, reqHeader).then(function(data) {
            /* TODO after delete success */
            $scope.goBack('/topology');
          });
        }
        
      } else if (modalData.action == 'submit') {
        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId+'/submit',
          noTrailingSlash: true
        };
        if('fabric' == $scope.source) {
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, modalData.submitData, reqHeader).then(function(data) {
            $scope.topology.submit = $scope.topologyData.submit = true;
            $log.debug('Fabric Submitted.');
            ngToast.create({
              className: 'success',
              content: 'Fabric Submitted Successfully.'
            });
          });
        } else if('topology' == $scope.source) {
          appServices.doAPIRequest(appSettings.appAPI.topology.edit, modalData.submitData, reqHeader).then(function(data) {
            $log.debug('Topology Submitted.');
            ngToast.create({
              className: 'success',
              content: 'Topology Submitted Successfully.'
            });
            $scope.goBack('/topology');
          });
        }
      } else if (modalData.action == 'clear') {
        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId+'/clear',
          noTrailingSlash: true
        };
        appServices.doAPIRequest(appSettings.appAPI.topology.edit, modalData.submitData, reqHeader).then(function(data) {
          $log.debug('Topology cleared.');
          ngToast.create({
            className: 'success',
            content: 'Topology cleared.'
          });
          $scope.getTierCount();
          $scope.viewAddedSwitches(data);
        });
      } else if (modalData.action == 'editConfig') {
        
        var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId+"/profiles",
          noTrailingSlash: true
        };

        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, modalData.submitData, reqHeader).then(function(data) {
          debugger;
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.tierCounter = 0;
          $scope.getLinkDetails();
          $scope.getSwitchDetails('reloadTopology');
        });
      }
    };

    angular.element('#topology_svg').ready(function() {
      $log.debug(angular.element('#topology_svg'));
      $log.debug('Document Loaded');
      $scope.init();
    });


    $scope.$watch(function() {
        return $rootScope.errorFlag;
    },function() {
        if($rootScope.errorFlag == true) {
          $scope.topologyData = angular.copy($scope.topology);
        }
    });

  });

angular.module('PoapServer').controller('AlertModalCtrl',
  function($scope, $modalInstance, appSettings, appServices, dataToModal) {

    $scope.heading = dataToModal.action;
    $scope.message = dataToModal.message;

    $scope.ok = function() {
      $modalInstance.close({
        action: dataToModal.action,
        id: dataToModal.id,
        index: dataToModal.index
      });
    };

    $scope.cancel = function() {
      $modalInstance.dismiss('cancel');
    };

  });

angular.module('PoapServer').controller('AddSwitchModalCtrl',
  function($scope, $modalInstance, appSettings, appServices, dataToModal) {
    $scope.source = dataToModal.source;
    $scope.action = dataToModal.action;
    $scope.submitData = {
      "switches" : [
        { 'tier': 'Spine', 'tier_display': 'Spine', 'count': 0 },
        { 'tier': 'Leaf', 'tier_display': 'Leaf', 'count': 0 },
        { 'tier': 'Core', 'tier_display': 'Core Router', 'count': 0 },
        {'tier': 'Border', 'tier_display': 'Border Router', 'count': 0}
      ]
    };

    $scope.ok = function() {
      $modalInstance.close({
          submitData : $scope.submitData,
          action : $scope.action
      });
    };

    $scope.cancel = function() {
      $modalInstance.dismiss('cancel');
    };

  });
  angular.module('PoapServer').controller('TopologyDefaultCtrl',
      function($scope, $modalInstance, appSettings, appServices, dataToModal){
        $scope.action = dataToModal.action;
        $scope.defaultEdit = dataToModal.defaultEdit;
        $scope.source = dataToModal.source;

        $scope.show = {
          'Core': false,
          'Border': false
        };

        $scope.selectList = {
          'imglist' : [],
          'linkTypes' : [
              {'name':'PHYSICAL','id':'Physical'},
              {'name':'PORT_CHANNEL', 'id':'Port-Channel'},
              {'name':'VPC_PEER','id':'VPC-Peer'},
              {'name':'VPC_MEMBER', 'id':'VPC-Member'}
            ]
        };

        var tierData = {
          'Core' : { 'tier': 'Core', 'tier_display': 'Core Router', 'model': '', 'image_profile': '' },
          'Border' : { 'tier': 'Border', 'tier_display': 'Border Router', 'model': '', 'image_profile': '' }
        };

        $scope.submitData = angular.copy(dataToModal.topology);

        $scope.fetchTierSwitches = function(tier) {
          var reqHeader = {
                appendToURL : true,
                value : "?tier="+tier,
                noTrailingSlash : true
            };
          appServices.doAPIRequest(appSettings.appAPI.switches.list, null, reqHeader).then(function(data) {
            $scope.selectList[tier] = data;
          });
        };

        $scope.changeAction = function(newAction) {
          if('edit' == newAction) {
            $scope.defaultEdit = true;
          }
        };

        $scope.addTier = function(tier) {
          $scope.submitData.defaults.switches.push(tierData[tier]);
          $scope.show[tier] = true;
        }

        $scope.init = function() {
          this.fetchTierSwitches('Core');
          this.fetchTierSwitches('Spine');
          this.fetchTierSwitches('Leaf');
          this.fetchTierSwitches('Border');
          var coreDefault = {};
          var borderDefault = {};

          var reqHeader = {
                appendToURL : true,
                value : '?state=true',
                noTrailingSlash : true
            };
          appServices.doAPIRequest(appSettings.appAPI.images.list, null, reqHeader).then(function(data) {
            $scope.selectList.imglist = data;
          });

          $scope.submitData.defaults.switches = $scope.submitData.defaults.switches.filter(function(a){
            if(a.tier == 'Core') {
              a.tier_display = 'Core Router';
              coreDefault = a;
              $scope.show[a.tier] = true;
            }
            if(a.tier == 'Border') {
              a.tier_display = 'Border Router';
              borderDefault = a;
              $scope.show[a.tier] = true;
            }
            if(a.tier == 'Spine') {
              a.tier_display = 'Spine';
            }
            if(a.tier == 'Leaf') {
              a.tier_display = 'Leaf';
            }
            return a;
          });
        };

        $scope.ok = function() {
          $modalInstance.close({
                submitData : $scope.submitData,
                action : $scope.action
            });
          if('fabric' == $scope.source) {
            $('#myModalWarn').modal('toggle');
          }
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.init();
  });
angular.module('PoapServer').controller('FabricConfigCtrl',
      function($scope, $modalInstance, appSettings, appServices, dataToModal){
        debugger;
        $scope.action = dataToModal.action;
        $scope.configEdit = dataToModal.configEdit;
        $scope.source = dataToModal.source;

        $scope.requestData = {
          "profiles" : []
        };
        $scope.selectList = {
          'config_list' : angular.copy(dataToModal.config_list),
          'fabricProfile_list' : angular.copy(dataToModal.fabricProfile_list),
          'workflow_list' : angular.copy(dataToModal.workflow_list)
        };
        $scope.submitData = angular.copy(dataToModal.topology.defaults);

        $scope.changeAction = function(newAction) {
          if('edit' == newAction) {
            $scope.configEdit = true;
          }
        };

        $scope.transformData = function() {
          $scope.requestData.config_profile = $scope.submitData.config_profile;
          $scope.requestData.feature_profile = $scope.submitData.feature_profile;
          $scope.requestData.profiles = $scope.submitData.switches;
        };

        $scope.ok = function() {
          
          this.transformData();
          $modalInstance.close({
                submitData : $scope.requestData,
                action : $scope.action
            });
        };

        $scope.init = function() {
          var defaultVal = {"id" : 0, "name" : "--None--"};
          $scope.submitData.config_profile = angular.copy(dataToModal.topology.config_profile);
          $scope.submitData.feature_profile = angular.copy(dataToModal.topology.feature_profile);
          $scope.selectList.config_list.unshift(defaultVal);
          $scope.selectList.fabricProfile_list.unshift(defaultVal);
          $scope.selectList.workflow_list.unshift(defaultVal);
        };

        $scope.checkTierValidity = function(index) {
            if(0 == $scope.submitData.switches[index].config_profile && 0 == $scope.submitData.switches[index].feature_profile) {
                $scope.addFabricForm["config_profile"+index].$setValidity('required',false);
                $scope.addFabricForm["feature_profile"+index].$setValidity('required',false);
                $('.profile-note').addClass('noteHighlight');
            } else {
                $scope.addFabricForm["config_profile"+index].$setValidity('required',true);
                $scope.addFabricForm["feature_profile"+index].$setValidity('required',true);
                $('.profile-note').removeClass('noteHighlight');
            }
            if((0 == $scope.submitData.switches[0].feature_profile && 0 == $scope.submitData.switches[1].feature_profile) || (0 != $scope.submitData.switches[0].feature_profile && 0 != $scope.submitData.switches[1].feature_profile)) {
                $scope.addFabricForm["feature_profile0"].$setValidity('required',true);
                $scope.addFabricForm["feature_profile1"].$setValidity('required',true);
            } else {
                $scope.addFabricForm["feature_profile0"].$setValidity('required',false);
                $scope.addFabricForm["feature_profile1"].$setValidity('required',false);
            }
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.init();
  });