'use strict';

/**
 * Checklist-model
 * AngularJS directive for list of checkboxes
 * https://github.com/vitalets/checklist-model
 * License: MIT http://opensource.org/licenses/MIT
 */

angular.module('checklist-model', [])
.directive('checklistModel', ['$parse', '$compile', function($parse, $compile) {
  // contains
  function contains(arr, item, comparator) {
    if (angular.isArray(arr)) {
      for (var i = arr.length; i--;) {
        if (comparator(arr[i], item)) {
          return true;
        }
      }
    }
    return false;
  }

  // add
  function add(arr, item, comparator) {
    arr = angular.isArray(arr) ? arr : [];
      if(!contains(arr, item, comparator)) {
          arr.push(item);
      }
    return arr;
  }  

  // remove
  function remove(arr, item, comparator) {
    if (angular.isArray(arr)) {
      for (var i = arr.length; i--;) {
        if (comparator(arr[i], item)) {
          arr.splice(i, 1);
          break;
        }
      }
    }
    return arr;
  }

  // http://stackoverflow.com/a/19228302/1458162
  function postLinkFn(scope, elem, attrs) {
     // exclude recursion, but still keep the model
    var checklistModel = attrs.checklistModel;
    attrs.$set("checklistModel", null);
    // compile with `ng-model` pointing to `checked`
    $compile(elem)(scope);
    attrs.$set("checklistModel", checklistModel);

    // getter / setter for original model
    var getter = $parse(checklistModel);
    var setter = getter.assign;
    var checklistChange = $parse(attrs.checklistChange);

    // value added to list
    var value = attrs.checklistValue ? $parse(attrs.checklistValue)(scope.$parent) : attrs.value;


    var comparator = angular.equals;

    if (attrs.hasOwnProperty('checklistComparator')){
      if (attrs.checklistComparator[0] == '.') {
        var comparatorExpression = attrs.checklistComparator.substring(1);
        comparator = function (a, b) {
          return a[comparatorExpression] === b[comparatorExpression];
        }
        
      } else {
        comparator = $parse(attrs.checklistComparator)(scope.$parent);
      }
    }

    // watch UI checked change
    scope.$watch(attrs.ngModel, function(newValue, oldValue) {
      if (newValue === oldValue) { 
        return;
      } 
      var current = getter(scope.$parent);
      if (angular.isFunction(setter)) {
        if (newValue === true) {
          setter(scope.$parent, add(current, value, comparator));
        } else {
          setter(scope.$parent, remove(current, value, comparator));
        }
      }

      if(!(current === undefined || current === null || current === '' || current.length === 0)) {
        var i =0;
        while(scope.switchForm !== undefined && scope.switchForm['tiers_'+i] !== undefined){
            scope.switchForm['tiers_'+i].$setValidity('required',true);
            i++;
        }
      } else {
        var i =0;
        while(scope.switchForm !== undefined && scope.switchForm['tiers_'+i] !== undefined){
            scope.switchForm['tiers_'+i].$setValidity('required',false);
            i++;
        }
      }

      if (checklistChange) {
        checklistChange(scope);
      }
    });
    
    // declare one function to be used for both $watch functions
    function setChecked(newArr, oldArr) {
        scope[attrs.ngModel] = contains(newArr, value, comparator);
    }

    // watch original model change
    // use the faster $watchCollection method if it's available
    if (angular.isFunction(scope.$parent.$watchCollection)) {
        scope.$parent.$watchCollection(checklistModel, setChecked);
    } else {
        scope.$parent.$watch(checklistModel, setChecked, true);
    }
  }

  return {
    restrict: 'A',
    priority: 1000,
    terminal: true,
    scope: true,
    compile: function(tElement, tAttrs) {
      if ((tElement[0].tagName !== 'INPUT' || tAttrs.type !== 'checkbox')
          && (tElement[0].tagName !== 'MD-CHECKBOX')
          && (!tAttrs.btnCheckbox)) {
        throw 'checklist-model should be applied to `input[type="checkbox"]` or `md-checkbox`.';
      }

      if (!tAttrs.checklistValue && !tAttrs.value) {
        throw 'You should provide `value` or `checklist-value`.';
      }

      // by default ngModel is 'checked', so we set it if not specified
      if (!tAttrs.ngModel) {
        // local scope var storing individual checkbox model
        tAttrs.$set("ngModel", "checked");
      }

      return postLinkFn;
    }
  };
}]);

/**
 * @ngdoc overview
 * @name PoapServer
 * @description
 * # PoapServer
 *
 * Main module of the application.
 */
var app = angular.module('PoapServer', [
    'ngAnimate',
    'ngAria',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap',
    'ui.bootstrap.tpls',
    'ngTable',
    'angular-bootstrap-select',
    'angular-svg-round-progress',
    'file-model',
    'filereader',

    //External Modules
    'angular-storage',
    'angular-loading-bar',

    //Translation Module
    'gettext',

    //Charts
    "chart.js",

    //ngToast
    'ngToast',

    //topologyModule
    "topologyModule",

    //for checkboxes
    "checklist-model"
]); 

app.config(function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'pages/common/views/login.html',
            controller: 'LoginCtrl'
        })
        .when('/register', {
            templateUrl: 'pages/common/views/register.html',
            controller: 'RegisterCtrl'
        })
        .when('/configlets', {
            templateUrl: 'pages/views/configlets.html',
            controller: 'ConfigletsCtrl',
            activemenu:'resources',
            activetab: 'configlets'
        })
        .when('/switches', {
            templateUrl: 'pages/views/switches.html',
            controller: 'SwitchesCtrl',
            activemenu:'switch',
            activetab: 'switches'
        })
        .when('/linecards', {
            templateUrl: 'pages/views/linecards.html',
            controller: 'LinecardCtrl',
            activemenu: 'switch',
            activetab: 'linecards'
        })
        .when('/images', {
            templateUrl: 'pages/views/images.html',
            controller: 'ImagesCtrl',
            activemenu: 'switch',
            activetab: 'images'
        })
        .when('/pools', {
            templateUrl: 'pages/views/pools.html',
            controller: 'PoolCtrl',
            activemenu:'resources',
            activetab: 'pools'
        })
        .when('/configuration', {
            templateUrl: 'pages/views/configuration.html',
            controller: 'ConfigurationCtrl',
            activemenu:'resources',
            activetab: 'configuration'
        })
        .when('/constructs/:mode', {
            templateUrl: 'pages/views/constructs.html',
            controller: 'ConstructCtrl',
            activemenu:'resources',
            activetab: 'configuration'
        })
        .when('/constructs/:mode/:id', {
            templateUrl: 'pages/views/constructs.html',
            controller: 'ConstructCtrl',
            activemenu:'resources',
            activetab: 'configuration'
        })

        .when('/topology', {
            templateUrl: 'pages/views/topology.html',
            controller: 'TopologyCtrl',
            activemenu:'fabric',
            activetab: 'topology'
        })
        .when('/topology/:mode/:topologyId', {
            templateUrl: 'pages/views/addTopology.html',
            controller: 'AddTopologyCtrl',
            activemenu:'fabric',
            activetab: 'topology'
        })
        .when('/discoveryRule', {
            templateUrl: 'pages/views/discoveryRule.html',
            controller: 'DiscoveryRuleCtrl',
            activemenu:'fabric',
            activetab: 'discoveryRule'
        })
        .when('/fabricInstance', {
            templateUrl: 'pages/views/fabricInstance.html',
            controller: 'FabricInstanceCtrl',
            activemenu:'fabric',
            activetab: 'fabrics'
        })
        .when('/fabricInstance/:mode/:fabricInstanceId', {
            templateUrl: 'pages/views/addTopology.html',
            controller: 'AddTopologyCtrl',
            activemenu:'fabric',
            activetab: 'fabrics'
        })

        .when('/deployedFabrics', {
            templateUrl: 'pages/views/deployedFabricList.html',
            controller: 'DeployedFabricCtrl',
            activemenu:'deployed',
            activetab: 'deployedFabric'
        })

        .when('/deployedFabrics/:fabricID/:replicaNumber', {
            templateUrl: 'pages/views/replicaDetails.html',
            controller: 'FabricReplicaCtrl',
            activemenu:'deployed',
            activetab: 'deployedFabric'
        })

        .when('/deployedSwitches', {
            templateUrl: 'pages/views/deployedSwitches.html',
            controller: 'DeployedSwitchesCtrl',
            activemenu:'fabric',
            activetab: 'deployedSwitches'
        })

        .when('/profileTemplate', {
            templateUrl: 'pages/views/profileTemplates.html',
            controller: 'ProfileTemplatesCtrl',
            activemenu:'resources',
            activetab: 'profileTemplate'
        })

        .when('/fabricProfile', {
            templateUrl: 'pages/views/fabricProfile.html',
            controller: 'FabricProfileCtrl',
            activemenu:'resources',
            activetab: 'fabricProfile'
        })

        .when('/fabricProfile/:mode', {
            templateUrl: 'pages/views/fabricProfileAddEdit.html',
            controller: 'FabricProfileAddEdit',
            activemenu:'resources',
            activetab: 'fabricProfile'
        })

        .when('/fabricProfile/:mode/:id', {
            templateUrl: 'pages/views/fabricProfileAddEdit.html',
            controller: 'FabricProfileAddEdit',
            activemenu:'resources',
            activetab: 'fabricProfile'
        })
        .when('/task', {
            templateUrl: 'pages/views/task.html',
            controller: 'TaskCtrl',
            activemenu:'resources',
            activetab: 'task'
        })
        .when('/workflow',{
            templateUrl: 'pages/views/workflow.html',
            controller: 'WorkflowCtrl',
            activemenu: 'resources',
            activetab: 'workflow'
        })
        .when('/workflow/:mode', {
            templateUrl: 'pages/views/addWorkflow.html',
            controller: 'AddWorkflowCtrl',
            activemenu:'resources',
            activetab: 'workflow'
        })
        .when('/workflow/:mode/:id', {
            templateUrl: 'pages/views/addWorkflow.html',
            controller: 'AddWorkflowCtrl',
            activemenu:'resources',
            activetab: 'workflow'
        })
        .when('/aaaServer',{
            templateUrl: 'pages/views/aaa.html',
            controller: 'AAA_Ctrl',
            activemenu: 'admin',
            activetab: 'aaa'
        })
        .when('/users',{
            templateUrl: 'pages/views/users.html',
            controller: 'UsersCtrl',
            activemenu: 'admin',
            activetab: 'users'
        })
        .when('/backup',{
            templateUrl: 'pages/views/backup.html',
            controller: 'BackupCtrl',
            activemenu: 'admin',
            activetab: 'backup'
        })
        .when('/group',{
            templateUrl: 'pages/views/groups.html',
            controller: 'GroupsCtrl',
            activemenu: 'manage',
            activetab: 'group'
        })
        .when('/group/:mode', {
            templateUrl: 'pages/views/group.html',
            controller: 'GrpCtrl',
            activemenu:'manage',
            activetab: 'group'
        })
        .when('/group/:mode/:id', {
            templateUrl: 'pages/views/group.html',
            controller: 'GrpCtrl',
            activemenu:'manage',
            activetab: 'group'
        })
        .when('/jobs', {
            templateUrl: 'pages/views/jobList.html',
            controller: 'JobsCtrl',
            activemenu:'manage',
            activetab: 'job'
        })
        .when('/job/:mode', {
            templateUrl: 'pages/views/job.html',
            controller: 'Job_Ctrl',
            activemenu:'manage',
            activetab: 'job'
        })
        .when('/job/:mode/:id', {
            templateUrl: 'pages/views/job.html',
            controller: 'Job_Ctrl',
            activemenu:'manage',
            activetab: 'job'
        })
        .when('/rma',{
            templateUrl: 'pages/views/rma.html',
            controller: 'RMA_Ctrl',
            activemenu: 'fabric',
            activetab: 'rma'
        })
        .otherwise({
            redirectTo: '/'
        });

        /*
        */
});


app.config(['ngToastProvider', function(ngToast) {
  ngToast.configure({
    verticalPosition: 'top',
    horizontalPosition: 'center',
    maxNumber: 10
  });
}]);
