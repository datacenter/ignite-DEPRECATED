'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:LoginCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
.controller('LoginCtrl', function($scope, $location, appSettings, appServices, $modal, $log, lclStorage) {
       $scope.$parent.bodyClass = "loginBody";
       $scope.$parent.isLogin = true;
       $scope.submit = {
             "username": "",
             "password" : ""
       };

        $scope.login = function() {
        	appServices.doAPIRequest(appSettings.appAPI.users.login, $scope.submit, null).then(function(data){
                // {"non_field_errors":["Unable to login with provided credentials."]}
                if(typeof data.non_field_errors != 'undefined') {
                    return;
                }
                else {
                    var loginDetails = {
                        "username" : $scope.submit.username,
                        "auth_token" : data.auth_token
                    }
                    lclStorage.set('userDetails', loginDetails);
                    $location.path('configlets');
                }


        	})
        }


});
