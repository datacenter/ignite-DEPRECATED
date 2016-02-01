angular.module('PoapServer')

app.controller('HeaderCtrl', function($scope, $location, lclStorage, appServices, appSettings,$route) {

	$scope.$route = $route;
	$scope.userID = lclStorage.get('userID');
    $scope.userDetails = lclStorage.get('userDetails');
});
