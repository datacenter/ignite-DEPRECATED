'use strict';

/**
 * @ngdoc function
 * @name PoapServer.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the PoapServer
 */
angular.module('PoapServer')
    .controller('MainCtrl', function($scope, $location, $http, $routeParams, $filter, $rootScope, $modal, $log, appSettings, appServices, gettextCatalog, lclStorage) {
    	$scope.appSettings = appSettings;
    	$scope.appServices = appServices;

    	$scope.deleteError = function($index){
			appServices.errors.splice($index, 1);
		}

        $scope.logout = function() {
            debugger;
            var dataToSubmit = {
                "username" : lclStorage.valueOf('InternalStore').inMemoryCache.userDetails.username
            };
            $scope.appServices.doAPIRequest($scope.appSettings.appAPI.users.logout, dataToSubmit, null).then(function(data) {
                //$scope.init('add');
                lclStorage.remove('userDetails');
            });
        };

        $scope.checklogin = function() {
        	var userDetails = lclStorage.get('userDetails');
            var location = $location.path();
            if(userDetails == null && location.indexOf('register') == -1) {
        		$location.path('#')
        	}
        }

        $scope.init = function() {
        	$scope.checklogin();
        }

        $scope.openErrorModal = function() {
                $scope.modalInstance = $modal.open({
                    animation: $scope.animationsEnabled,
                    templateUrl: 'pages/template/modal/errorModal.html',
                    controller: 'errorModalCtrl',
                    size: 'md',
                    backdrop: 'static'
                });
                $scope.modalInstance.result.then(function() {
                    appServices.clearErrors();
                }, function() {
                    appServices.clearErrors();
                    $log.info('Modal dismissed at: ' + new Date());
                });
        };

        /* watch for the error flag */

        $scope.$watch(function() {
            return $rootScope.errorFlag;
        },function() {
            if($rootScope.errorFlag == true)
                $scope.openErrorModal();
        });

        $scope.init();

});







