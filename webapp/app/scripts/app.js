'use strict';

/**
 * Checklist-model
 * AngularJS directive for list of checkboxes
 * https://github.com/vitalets/checklist-model
 * License: MIT http://opensource.org/licenses/MIT
 */

// angular.module('checklist-model', [])


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
    "topologyModule"
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
            activemenu: 'fabric',
            activetab: 'group'
        })
        .when('/group/:mode', {
            templateUrl: 'pages/views/group.html',
            controller: 'GrpCtrl',
            activemenu:'fabric',
            activetab: 'group'
        })
        .when('/group/:mode/:id', {
            templateUrl: 'pages/views/group.html',
            controller: 'GrpCtrl',
            activemenu:'fabric',
            activetab: 'group'
        })
        .when('/jobs', {
            templateUrl: 'pages/views/jobList.html',
            controller: 'JobsCtrl',
            activemenu:'fabric',
            activetab: 'job'
        })
        .when('/job/:mode', {
            templateUrl: 'pages/views/job.html',
            controller: 'Job_Ctrl',
            activemenu:'fabric',
            activetab: 'job'
        })
        .when('/job/:mode/:id', {
            templateUrl: 'pages/views/job.html',
            controller: 'Job_Ctrl',
            activemenu:'fabric',
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
