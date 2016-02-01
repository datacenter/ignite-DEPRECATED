angular.module('PoapServer').controller('errorModalCtrl',
function($scope,$modalInstance, $rootScope, appServices) {
    $scope.appServices = appServices;
    $scope.ok = function() {
        $modalInstance.dismiss('cancel');
    };
});