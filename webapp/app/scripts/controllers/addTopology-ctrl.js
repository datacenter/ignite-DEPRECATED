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

    $scope.disc_leave_flag = false;
    $scope.switchDetails = {
      'defaults_switch_name':[],
      'default_switches':[],
      'selectList':{
        'config_type_list':appSettings.fieldValues.fabric.switch_config
      },
      'vpc_connected':[],
      'curLink':{},
      'count' : {
        'Core' : 0,
        'Spine': 0,
        'Leaf' : 0,
        'Border': 0,
      }
    };

    $scope.addLink = {};

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

    $scope.cloneTopo = function() {
      $scope.action = "clone";
      $scope.openCloneModal();
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

    $scope.openCloneModal = function(size) {
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/cloneModal.html',
            controller: 'TopologyCloneModalCtrl',
            size: 'sm',
            resolve: {
                dataToModal : function() {
                    return {
                        action : $scope.action,
                        id : $scope.selectedId,
                        source : $scope.source
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

    $scope.goBackToList = function() {
      var path = '/topology';
      if('fabric' == $scope.source) {
        path = '/fabricInstance';
      }
      this.goBack(path);
    };

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
            "workflow": $scope.topologyData.switches[index].workflow,
            "config_type": $scope.topologyData.switches[index].config_type
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
    $scope.delAction = 'delete';

    $scope.deleteSwitch = function(id, action) {

      $('#confirmDelLabel').html('Confirm '+action);
      $('#popEdit_Item_'+id).modal('toggle');
      if(action == 'delete') {
        $('#modalDeleteContent').html('Are you sure you want to delete this switch?'); 
      } else {
        $('#modalDeleteContent').html('Are you sure you want to decommission this switch and delete any generated config files?'); 
      }
      $scope.toDeleteItem = id;
      $scope.itemType = 'switch';
      $scope.delAction = action;
      $('#myModalDelete').modal('toggle');
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
      if($scope.itemType == 'switch' && $scope.delAction == 'decommission') {
        valToAppend = valToAppend+"/decommission"
      }
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

    $scope.closeAddLink = function(){
      $('#alertLinkExists').hide();
      $('#vpcLinkNotAllowed').hide();
      $('#memLinkNotAllowed').hide();
      $('#alertLinkSame').hide();
      $scope.addLink.src_switch="";
      $scope.addLink.dst_switch="";
    };

    $scope.addLinkModal = function(linkFor) {
      $scope.switchDetails.curLink = {};
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
      var foundFlag = false;
      $log.debug('src_switch and dst_switch');
      $scope.switchDetails.curLink = linkObj;
      var src_switch = linkObj.src_switch;
      var dst_switch = linkObj.dst_switch;
      var link_type = linkObj.link_type;
      console.log(linkObj.src_switch);
      console.log(linkObj.dst_switch);
      console.log(linkObj.link_type);

      if (!(src_switch == undefined || src_switch == "") && !(dst_switch == undefined || dst_switch == "") && linkObj.link_type != undefined && linkObj.num_links > 0 && linkObj.num_links < 9) {

      if (src_switch == dst_switch) {
        $('#alertLinkSame').show();
        return false;
      } else {
        $('#alertLinkSame').hide();
      }
      $('#vpcLinkNotAllowed').hide();
      $('#alertLinkExists').hide();
      $('#memLinkNotAllowed').hide();
      if(link_type == 'VPC-Peer') {
        $scope.switchDetails.vpc_connected.filter(function(a){
          if(a.id == src_switch || a.id == dst_switch) {
            $('#vpcLinkNotAllowed').show();
            foundFlag = true;
          }
        });
        if(foundFlag) {
          return false;
        }
      } else if(link_type == 'VPC-Member') {
        $('#vpcLinkNotAllowed').hide();
        for (var i = 0; i < $scope.topology.links.length; i++) {
          if (($scope.topology.links[i].src_switch == src_switch && $scope.topology.links[i].dst_switch == dst_switch) || ($scope.topology.links[i].src_switch == dst_switch && $scope.topology.links[i].dst_switch == src_switch)) {
            foundFlag = true;
          }
        }
        if(!foundFlag) {
          $('#memLinkNotAllowed').show();
          return false;
        } else {
          $('#memLinkNotAllowed').hide();
        }
      } else {
        $('#vpcLinkNotAllowed').hide();
        for (var i = 0; i < $scope.topology.links.length; i++) {
          if (($scope.topology.links[i].src_switch == src_switch && $scope.topology.links[i].dst_switch == dst_switch) || ($scope.topology.links[i].src_switch == dst_switch && $scope.topology.links[i].dst_switch == src_switch)) {
            $('#alertLinkExists').show();
            return false;
          } else {
            $('#alertLinkExists').hide();
          }
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
        $scope.topology = data;
        $scope.topologyData = angular.copy($scope.topology);
        $scope.viewAddedSwitches(data);
        if('VPC-Peer' == $scope.switchDetails.curLink.link_type) {
          $scope.switchDetails.vpc_connected.push({id:$scope.switchDetails.curLink.src_switch},{id:$scope.switchDetails.curLink.dst_switch});
        }
        $scope.switchDetails.curLink = {};
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
      if('edit' == action || 'add_switch' == action || 'clone' == action) {
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
      if('edit' == action || 'add_switch' == action || 'clone' == action) {
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
      $('#popEdit_Item_'+statId).modal('toggle');
      $scope.modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/fabricConfigView.html',
        controller: 'DeployedSwitchConfigModalCtrl',
        size: 'lg',
        backdrop: 'static',
        resolve: {
            dataToModal : function() {
                return {
                    "statId" : statId,
                    "type" : "depConfig"
                }
            }
         }
      });
      $scope.modalInstance.result.then(function(modalData) {
        $timeout(function() {
          $('#popEdit_Item_'+statId).modal('toggle');
        },500);
         $log.info('Modal dismissed at: ' + new Date());
      }, function() {
          $timeout(function() {
            $('#popEdit_Item_'+statId).modal('toggle');
          },500);
          $log.info('Modal dismissed at: ' + new Date());
      });
    };

    $scope.openConfigHistory = function(switch_id) {
      $('#popEdit_Item_'+switch_id).modal('toggle');
      $scope.modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/configVersions.html',
        controller: 'ConfigHistoryModalCtrl',
        size: 'lg',
        backdrop: 'static',
        resolve: {
            dataToModal : function() {
                return {
                    "switch_id" : switch_id,
                    "fabricId" : $scope.selectedId
                }
            }
         }
      });
      $scope.modalInstance.result.then(function(modalData) {
        $timeout(function() {
         $('#popEdit_Item_'+switch_id).modal('toggle');
        },500);
         $log.info('Modal dismissed at: ' + new Date());
      }, function() {
          $timeout(function() {
            $('#popEdit_Item_'+switch_id).modal('toggle');
          },500);
         $log.info('Modal dismissed at: ' + new Date());
      });
    };

    $scope.openSwitchPullConfigModal = function(statId) {
      $('#popEdit_Item_'+statId).modal('toggle');
      $scope.modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'pages/template/modal/fabricConfigView.html',
        controller: 'DeployedSwitchConfigModalCtrl',
        size: 'lg',
        backdrop: 'static',
        resolve: {
            dataToModal : function() {
                return {
                    "statId" : statId,
                    "fabricId" : $scope.selectedId,
                    "type" : "pullConfig"
                }
            }
         }
      });
      $scope.modalInstance.result.then(function(modalData) {
         $timeout(function() {
          $('#popEdit_Item_'+statId).modal('toggle');
        },500);
         $log.info('statId Modal dismissed at: ' + new Date());
      }, function() {
          $timeout(function() {
            $('#popEdit_Item_'+statId).modal('toggle');
          },500);
          $log.info(statId+' Modal dismissed at: ' + new Date());
      });
    };

    $scope.openDepSwitchLogModal = function(statId) {
      $('#popEdit_Item_'+statId).modal('toggle');
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
          $timeout(function() {
             $('#popEdit_Item_'+statId).modal('toggle');
           },500);
         $log.info('Modal dismissed at: ' + new Date());
      }, function() {
          $timeout(function() {
            $('#popEdit_Item_'+statId).modal('toggle');
          },500);
          $log.info('Modal dismissed at: ' + new Date());
      });
    };

    $scope.reset_switch = function(switch_id) {
      var reqHeader = {
                appendToURL : true,
                value : $scope.selectedId+"/switch/"+switch_id+"/resetbootdetail",
                noTrailingSlash : true
            };
      appServices.doAPIRequest(appSettings.appAPI.fabricInstance.reset_switch, null, reqHeader).then(function(data) {
       ngToast.create({
          className: 'success',
          content: 'Switch Reset, successful!.'
        });
        $scope.topology = data;
        $scope.topologyData = angular.copy($scope.topology);
        $scope.viewAddedSwitches(data);
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

      appServices.doAPIRequest(appSettings.appAPI.fabricInstance.all_config_profile, null, reqHeader).then(function(data) {
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

        if('VPC-Peer' == value.link_type) {
          $scope.switchDetails.vpc_connected.push({id:value.src_switch},{id:value.dst_switch});
        }

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

    $scope.viewMG = function() {
      $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/createFabGrpModal.html',
            controller: 'FabGroupsCtrl',
            size: 'lg',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        switches : $scope.topologyData.switches,
                        fabId : $scope.selectedId
                        /*action : action,
                        configEdit : $scope.configEdit,
                        topology : $scope.topology,
                        source : $scope.source,
                        config_list : $scope.switchDetails.selectList.config_list,
                        fabricProfile_list : $scope.switchDetails.selectList.fabricProfile_list,
                        workflow_list : $scope.switchDetails.selectList.workflow_list,
                        callerScope : $scope*/
                    }
                }
             }
        });
        $scope.modalInstance.result.then(function(modalData) {
            $scope.topologyData.maintenance_group_count = angular.copy(modalData.totalGrp);
            $scope.topology.maintenance_group_count = angular.copy(modalData.totalGrp);
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
      var reqHeader = {
          appendToURL: true,
          value: $scope.selectedId,
          noTrailingSlash: true
        };
      if(modalData.action === 'add_switch') {
        var requestHeader = angular.copy(reqHeader);
        requestHeader.value = requestHeader.value+"/switch";

        var addSwitchData = appSettings.appAPI.topology.add_switch_Link;
        if($scope.source == 'fabric') {
          addSwitchData = appSettings.appAPI.fabricInstance.add_switch_Link;
        }

        appServices.doAPIRequest(addSwitchData, modalData.submitData, requestHeader).then(function(data) {
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
      } else if (modalData.action == 'delete') {
        if('fabric' == $scope.source) {
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.delete, null, reqHeader).then(function(data) {
            /* TODO after delete success */
            $scope.goBack('/fabricInstance');
          });
        } else {
          appServices.doAPIRequest(appSettings.appAPI.topology.delete, null, reqHeader).then(function(data) {
            /* TODO after delete success */
            $scope.goBack('/topology');
          });
        }
        
      } else if (modalData.action == 'submit') {
        var requestHeader = angular.copy(reqHeader);
        requestHeader.value = requestHeader.value+"/submit";
        if('fabric' == $scope.source) {
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, modalData.submitData, requestHeader).then(function(data) {
            $scope.topology.submit = $scope.topologyData.submit = true;
            $log.debug('Fabric Submitted.');
            ngToast.create({
              className: 'success',
              content: 'Fabric Submitted Successfully.'
            });
          });
        } else if('topology' == $scope.source) {
          appServices.doAPIRequest(appSettings.appAPI.topology.edit, modalData.submitData, requestHeader).then(function(data) {
            $log.debug('Topology Submitted.');
            ngToast.create({
              className: 'success',
              content: 'Topology Submitted Successfully.'
            });
            $scope.goBack('/topology');
          });
        }
      } else if (modalData.action == 'clear') {
        var requestHeader = angular.copy(reqHeader);
        requestHeader.value = requestHeader.value+"/clear";
        appServices.doAPIRequest(appSettings.appAPI.topology.edit, modalData.submitData, requestHeader).then(function(data) {
          $log.debug('Topology cleared.');
          ngToast.create({
            className: 'success',
            content: 'Topology cleared.'
          });
          $scope.topology = data;
          $scope.topologyData = angular.copy(data);
          $scope.viewAddedSwitches(data);
          $scope.getTierCount();
        });
      } else if (modalData.action == 'editConfig') {
        var requestHeader = angular.copy(reqHeader);
        requestHeader.value = requestHeader.value+"/profiles";
        
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.edit, modalData.submitData, requestHeader).then(function(data) {
          $scope.topology = data;
          $scope.topologyData = angular.copy($scope.topology);
          $scope.tierCounter = 0;
          $scope.getLinkDetails();
          $scope.getSwitchDetails('reloadTopology');
        });
      } else if (modalData.action == 'clone') {
        var requestHeader = angular.copy(reqHeader);
        requestHeader.value = requestHeader.value+"/clone";
        if('fabric' == $scope.source) {
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.clone, modalData.submitData, requestHeader).then(function(data) {
            $location.path('/fabricInstance/edit/'+data.id);
          });
        } else {
          appServices.doAPIRequest(appSettings.appAPI.topology.clone, modalData.submitData, requestHeader).then(function(data) {
            $location.path('/topology/edit/'+data.id);
          });
        }
      } else if(modalData.action == 'add_discovery') {
          var requestHeader = angular.copy(reqHeader);
          requestHeader.value = requestHeader.value+"/save";
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.discovery_save,modalData.submitData,requestHeader).then(function(data){
              $scope.disc_leave_flag = true;
              $location.path('/fabricInstance/edit/'+$scope.selectedId);
          });
      } else if(modalData.action == 'del_discovery') {
          var requestHeader = angular.copy(reqHeader);
          requestHeader.value = requestHeader.value+"/delete";
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.discovery_delete,null,requestHeader).then(function(data){
              $scope.disc_leave_flag = true;
              $location.path('/fabricInstance');
          });
      }
    };

    $scope.saveDiscovery = function() {
        $scope.modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/addFabricModal.html',
            controller: 'FabricCreateCtrl',
            size: 'md',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    return {
                        action : 'add_discovery',
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

    angular.element('#topology_svg').ready(function() {
      $log.debug(angular.element('#topology_svg'));
      $log.debug('Document Loaded');
      $scope.init();
    });

    $scope.deleteDiscovery = function() {
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        id : $scope.selectedId,
                        action: 'del_discovery',
                        message: 'Are you sure you want to delete the discovery?',
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

    $scope.$on('$locationChangeStart', function( event ) {
        if($scope.topologyData.is_discovered === true && !$scope.topologyData.is_saved && !$scope.disc_leave_flag) {
          var answer = confirm("Leaving this page would delete this fabric. Do you want to continue?")
          if (answer) {
              var modalData = {
                action : 'del_discovery'
              }
              $scope.submitData(modalData);
          } else {
            event.preventDefault();
          }
        }
    });

    $scope.$watch(function() {
        return $rootScope.errorFlag;
    },function() {
        if($rootScope.errorFlag == true) {
          $scope.topologyData = angular.copy($scope.topology);
        }
    });

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
          angular.forEach($scope.selectList.config_list, function(val, key){
              val.name = val.name+' ('+val.version+')';
          });
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
angular.module('PoapServer').controller('FabGroupsCtrl',
    function($scope, $modalInstance, appSettings, appServices, dataToModal, $log, ngTableParams, $filter, $timeout, $modal){

      $scope.appServices = appServices;
      $scope.fabId = dataToModal.fabId;
      $scope.groupData = {
        name : '',
        username : '',
        password : '',
        switch_list : []
      }
      // $scope.view_type = "list";
      $scope.fab_switches = angular.copy(dataToModal.switches);
      $scope.core_switches = [];
      $scope.spine_switches = [];
      $scope.leaf_switches = [];
      $scope.border_switches = [];
      $scope.action = 'list';
      $scope.editGrpId = -1;
      $scope.searchSwitchKeyword = '';
      // $scope.switch_list = [];

      /**For groups table pagination**/
    $scope.tableParams = new ngTableParams({
          page: 1,
          count: appSettings.tableSettings.count,
          sorting: {
              "name": "asc"
          }
      }, {
          counts:[],
          getData: function($defer, params) {
              appServices.tablePagination($defer, $filter, params, $scope.groups, $scope.searchKeyword);
          }
      });

      $scope.toggleAnimation = function() {
          $scope.animationsEnabled = !$scope.animationsEnabled;
      };

      $scope.$watch("searchKeyword", function () {
          $scope.tableParams.reload();
          $scope.tableParams.page(1);
      });
      /** table **/

      $scope.init = function() {
        $scope.getGroupsList();
      };

      $scope.getGroupsList = function() {
        var reqHeader = {
          appendToURL: true,
          value: $scope.fabId,
          noTrailingSlash: true
        };
        appServices.doAPIRequest(appSettings.appAPI.group.list, null, reqHeader).then(function(data) {
            $scope.groups = data;
            $scope.transformData();
            $scope.tableParams.reload();
            $scope.view_type = "list";
            $scope.action = "list";
            $scope.totalGrp = data.length;
        });
      };

      $scope.transformData = function() {
        $scope.groups.filter(function(group){
            var switchlist = '';
            group.switch_list.filter(function(grpSwitch){
                switchlist = switchlist+grpSwitch.switch_name+', ';
            });
            switchlist = switchlist.substring(0,switchlist.length-2);
            if (switchlist.length > 50) {
              switchlist = switchlist.substring(0, 55) + '...';
              console.log('--------NEW Switch Name----------');
              console.log(switchlist);
            }
            group.switchlist = switchlist;
            return group;
        });
    };

    $scope.createGrp = function() {
      $scope.action = 'add';
      $scope.fetchSwitches();
      $scope.fab_switches.filter(function(modalSwitch){
        modalSwitch[modalSwitch.id] = false;
      });
      $scope.groupData = {
        name : '',
        username : '',
        password : '',
        switch_list : []
      }
    };

    $scope.switches = [];

      $scope.fetchSwitches = function() {
        var last_index = 0;
        $scope.switches = [];
        var tot_iter = Math.floor($scope.fab_switches.length / 3);
        var multiplier = 0;
        for(var i = 0; i < tot_iter; i++,multiplier++) {
          var switchRow = {
            'switch1' : $scope.fab_switches[(multiplier*3)],
            'switch2' : $scope.fab_switches[(1) + (multiplier*3)],
            'switch3' : $scope.fab_switches[(2) + (multiplier*3)]
          };
          $scope.switches.push(switchRow);
          var last_index = (2) + (multiplier*3);
        }
        var diff = (($scope.fab_switches.length - 1) - (last_index));
        if( diff > 0) {
          var switchRow = {
            'switch1' : null,
            'switch2' : null,
            'switch3' : null
          };
          if( diff == 1) {
            switchRow.switch1 = $scope.fab_switches[last_index + 1];
          } else {
            switchRow.switch1 = $scope.fab_switches[last_index + 1];
            switchRow.switch2 = $scope.fab_switches[last_index + 2]
          }
          $scope.switches.push(switchRow);
        }
        $scope.view_type = "addGrp";
        $scope.searchSwitchKeyword = "";
      };

      $scope.editGrp = function(grpId,action) {
        $scope.editGrpId = grpId;
        var reqHeader = {
          appendToURL: true,
          value: $scope.fabId+'/'+grpId,
          noTrailingSlash: true
        };
        $scope.fab_switches.filter(function(modalSwitch){
          modalSwitch[modalSwitch.id] = false;
        });
        appServices.doAPIRequest(appSettings.appAPI.group.getById, null, reqHeader).then(function(data) {
            $scope.groupData = angular.copy(data);
            $scope.grpSwitchList();
            $scope.fetchSwitches();
            $scope.action = action;
        });
      };

      $scope.changeAction = function(action) {
        $scope.action = action;
      };

      $scope.grpSwitchList = function() {
        var switchlist = $scope.groupData.switch_list;
        $scope.groupData.switch_list = [];
        switchlist.filter(function(swich){
          $scope.groupData.switch_list.push({'switch_id': swich.switch_id});
          $log.info(dataToModal);
          $scope.fab_switches.filter(function(modalSwitch){
            if(modalSwitch.id == swich.switch_id) {
              modalSwitch[modalSwitch.id] = true;
            }
          });
          //$scope.switch[swich.switch_name] = true;
        });
      };

      $scope.deleteGroup = function(grpId) {
          var modalInstance = $modal.open({
              animation: $scope.animationsEnabled,
              templateUrl: 'pages/template/modal/deleteModal.html',
              controller: 'AlertModalCtrl',
              size: 'md',
              backdrop: 'static',
              resolve: {
                  dataToModal : function() {
                      return {
                          id : grpId,
                          action: 'delete',
                          message: 'Are you sure you want to delete this group?',
                          callerScope : $scope
                      }
                  }
               }
          });

          modalInstance.result.then(function(modalData) {
              var requestHeader = {
                    appendToURL: true,
                    value: $scope.fabId+'/'+grpId,
                    noTrailingSlash: true
                };

                appServices.doAPIRequest(appSettings.appAPI.group.delete, null, requestHeader).then(function(data) {
                  $scope.getGroupsList();
                });

          }, function() {
              $log.info('Modal dismissed at: ' + new Date());
          });
      };

      $scope.save = function() {
        var reqHeader = {
          appendToURL: true,
          value: $scope.fabId,
          noTrailingSlash: true
        };
        
        appServices.doAPIRequest(appSettings.appAPI.group.create, $scope.groupData, reqHeader).then(function(data) {
          $scope.getGroupsList();
        });
        $log.info($scope.selectedSwitches);
      };

      $scope.update = function() {
        var reqHeader = {
          appendToURL: true,
          value: $scope.fabId+'/'+$scope.editGrpId,
          noTrailingSlash: true
        };
        
        appServices.doAPIRequest(appSettings.appAPI.group.edit, $scope.groupData, reqHeader).then(function(data) {
          $scope.getGroupsList();
        });
      };

      $scope.cancel = function() {
        if($scope.view_type == "list") {
          $modalInstance.close({
              totalGrp : $scope.totalGrp
          });
        } else {
          $scope.view_type = "list";
          $scope.action = "list";
        }
      };

      $scope.selectAllSwitches = function() {
        if($scope.sel_all) {
          $scope.fab_switches.filter(function(modalSwitch){
              modalSwitch[modalSwitch.id] = true;
          });
        } else {
          $scope.fab_switches.filter(function(modalSwitch){
              modalSwitch[modalSwitch.id] = false;
          });
        }
      };
    

      // Custom search method
      var fullName = '';
      /*$scope.searchSwitch = function(swich) {
        if ($scope.searchSwitchKeyword.length <= 0) return true;
        if(swich.switch2 != null && swich.switch3 != null) {
          var searchSwitchKeyword = (""+$scope.searchSwitchKeyword).toLowerCase(),
                fullName = [swich.switch1.id, swich.switch1.name, swich.switch1.serial_num, swich.switch2.id, swich.switch2.name, swich.switch2.serial_num, swich.switch3.id, swich.switch3.name, swich.switch3.serial_num].join(" ").toLowerCase();
          return fullName.indexOf(searchSwitchKeyword) > -1;
        } else if(swich.switch2 != null) {
          var searchSwitchKeyword = (""+$scope.searchSwitchKeyword).toLowerCase(),
                fullName = [swich.switch1.id, swich.switch1.name, swich.switch1.serial_num, swich.switch2.id, swich.switch2.name, swich.switch2.serial_num].join(" ").toLowerCase();
          return fullName.indexOf(searchSwitchKeyword) > -1;
        } else {
          var searchSwitchKeyword = (""+$scope.searchSwitchKeyword).toLowerCase(),
                fullName = [swich.switch1.id, swich.switch1.name, swich.switch1.serial_num].join(" ").toLowerCase();
          return fullName.indexOf(searchSwitchKeyword) > -1;
        }
      }*/

      $scope.searchSwitch = function(swich) {
        if ($scope.searchSwitchKeyword.length <= 0) return true;
        var searchSwitchKeyword = (""+$scope.searchSwitchKeyword).toLowerCase(),
                fullName = [swich.id, swich.name, swich.serial_num].join(" ").toLowerCase();
        return fullName.indexOf(searchSwitchKeyword) > -1;
      }

      $scope.init();
});

angular.module('PoapServer').controller('ConfigHistoryModalCtrl',
  function($scope, $modalInstance, appSettings, appServices, dataToModal, $log, ngTableParams, $filter, $timeout, $modal){

      $scope.appSettings = appSettings;
      $scope.appServices = appServices;
      $scope.fabricId = dataToModal.fabricId;
      $scope.switch_id = dataToModal.switch_id;

      $scope.config_versions = [];
      $scope.selected_config = [];
      $scope.config = {};


      /**For config history table pagination**/
    $scope.tableParams = new ngTableParams({
          page: 1,
          count: appSettings.tableSettings.count,
          sorting: {
              "name": "asc"
          }
      }, {
          counts:[],
          getData: function($defer, params) {
              appServices.tablePagination($defer, $filter, params, $scope.config_versions, $scope.searchKeyword);
          }
      });

      $scope.toggleAnimation = function() {
          $scope.animationsEnabled = !$scope.animationsEnabled;
      };

      $scope.$watch("searchKeyword", function () {
          $scope.tableParams.reload();
          $scope.tableParams.page(1);
      });
      /** table **/

      $scope.init = function() {
        $scope.view_type = 'list';

        var reqHeader = {
          appendToURL: true,
          value: $scope.fabricId+'/switch/'+$scope.switch_id+'/config',
          noTrailingSlash: true
        };
        
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.config_history, null, reqHeader).then(function(data) {
          $scope.config_versions = data;
          $scope.tableParams.reload();
        });
      };

      $scope.compare = function(config_list) {
        var reqHeader = {
          appendToURL: true,
          value: $scope.fabricId+'/switch/'+$scope.switch_id+'/config/'+config_list[0].id,
          noTrailingSlash: true
        };
        
        appServices.doAPIRequest(appSettings.appAPI.fabricInstance.fetch_config, null, reqHeader).then(function(data) {
          console.log(data);
          $scope.config.file1 = data;
          var reqHeader = {
            appendToURL: true,
            value: $scope.fabricId+'/switch/'+$scope.switch_id+'/config/'+config_list[1].id,
            noTrailingSlash: true
          };
          appServices.doAPIRequest(appSettings.appAPI.fabricInstance.fetch_config, null, reqHeader).then(function(data) {
            console.log(data);
            $scope.config.file2 = data;
            $scope.view_type = 'compare';
            $scope.diffUsingJS();
          });
        });
      };

      $scope.diffUsingJS = function () {
          // var byId = function (id) { return document.getElementById(id); },
          var  base = difflib.stringAsLines($scope.config.file1),
            newtxt = difflib.stringAsLines($scope.config.file2),
            sm = new difflib.SequenceMatcher(base, newtxt),
            opcodes = sm.get_opcodes(),
            diffoutputdiv = $("#diffoutput")[0];
            // contextSize = byId("contextSize").value;

          diffoutputdiv.innerHTML = "";
          // contextSize = contextSize || null;

          diffoutputdiv.appendChild(diffview.buildView({
            baseTextLines: base,
            newTextLines: newtxt,
            opcodes: opcodes,
            baseTextName: "Version "+$scope.selected_config[0].version,
            newTextName: "Version "+$scope.selected_config[1].version,
            contextSize: null,
            viewType: 0
          }));
        };

      $scope.cancel = function() {
        if($scope.view_type == 'list') {
          $modalInstance.dismiss('cancel');
        } else {
          $scope.view_type = 'list';
        }
      };

      $scope.init();

});