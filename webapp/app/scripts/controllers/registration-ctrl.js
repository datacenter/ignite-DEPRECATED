'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:LoginCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
.controller('RegisterCtrl', function($scope, $location, appSettings, appServices, $modal, $log, lclStorage) {
       $scope.$parent.bodyClass = "loginBody";
       $scope.$parent.isLogin = true;
       $scope.submit = {
             "username": "",
             "password" : "",
             "email" : "",
             "first_name" : "",
             "last_name" : ""
       };

       $scope.confrimPassword = "";
       $scope.passwordMatch = true;

       $scope.register = function() {   
            if($scope.confrimPassword != $scope.submit.password) {
                return;
            }

            appServices.doAPIRequest(appSettings.appAPI.users.register, $scope.submit, null).then(function(data){
                if(data.username == $scope.submit.username) {
                    $location.path('#');      
                }
            })
       };

       $scope.matchPassword = function() {
            if($scope.confrimPassword == $scope.submit.password) {
                $scope.passwordMatch = true;
            }
            else {
                $scope.passwordMatch = false;   
            }
       }

});
