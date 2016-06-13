'use strict';


angular.module('PoapServer')
  .controller('BackupCtrl', function($scope, $rootScope, $location, $filter, ngTableParams, appSettings, appServices, gettextCatalog, lclStorage, $modal, $log, roundProgressService, ngToast) {

    appServices.setInternalAppUI($scope);

    var parent = $scope.$parent;
    $scope.backups = [];
    $scope.selectedId = null;

    $scope.ok = function(){
        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/pleaseWait.html',
            controller: 'CreateBackupCtrl',
            size: 'sm',
            backdrop: 'static',
            resolve: {
                dataToModal : function() {
                    var dtm = {
                        action : 'backup'
                    };

                    return dtm;
                }
             }
        });

        modalInstance.result.then(function(modalData) {
            $scope.submitData(modalData);

        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.downloadFile = function(file_name) {
        var url = angular.copy(appSettings.appAPI.baseURL+appSettings.appAPI.backup.download.url+file_name.split('.')[0]);
        window.open(url);
        /*var reqHeader = {
            appendToURL : true,
            value : file_name.split('.')[0],
            noTrailingSlash : true
        };
        appServices.doAPIRequest(appSettings.appAPI.backup.download, null, reqHeader).then(function(data) {
            saveData(data, file_name);
        });*/
    };

    /*var saveData = (function () {
                var a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            return function (data, file_name) {
                var json = JSON.stringify(data),
                    blob = new Blob([json], {type: "octet/stream"}),
                    url = window.URL.createObjectURL(blob);
                a.href = url;
                a.download = file_name;
                a.click();
                window.URL.revokeObjectURL(url);
                };
            }());*/

    $scope.deleteBackup = function(id) {
        $scope.selectedId = id;

        var modalInstance = $modal.open({
            animation: $scope.animationsEnabled,
            templateUrl: 'pages/template/modal/deleteModal.html',
            controller: 'AlertModalCtrl',
            size: 'md',
            resolve: {
                dataToModal : function() {
                    return {
                        id: $scope.selectedId,
                        action: 'delete',
                        message: 'Are you sure you want to delete this backup?',
                        callerScope: $scope
                    }
                }
             }
        });

        modalInstance.result.then(function(modalData) {
            $scope.doDeleteBackup(modalData);

        }, function() {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.doDeleteBackup = function(modalData){
        /*var reqHeader = {
            appendToURL : true,
            value : $scope.selectedId,
            noTrailingSlash : true
        };*/
        $scope.files = {
            backup_files : []
        };
        var file = $scope.selectedId.toString();
        $scope.files.backup_files.push($scope.selectedId);
        appServices.doAPIRequest(appSettings.appAPI.backup.delete, $scope.files.backup_files, null).then(function(data) {
            $scope.init();
        });
    };

    $scope.submitData = function(){
        ngToast.create({
          className: 'success',
          content: 'Backup Created Successfully.'
        });
        $scope.init();
    };

    $scope.fetchBackups = function() {
         appServices.doAPIRequest(appSettings.appAPI.backup.list, null, null).then(function(data) {
            var backup_list = data;
            backup_list.filter(function(a){
                var item = {
                    "name": a,
                    "time": a.split('.')[0]
                };
                $scope.backups.push(item);
            });
            $scope.backups = $scope.backups.filter(function(a){
                var date = a.time.split('_');
                var newDate = date[2]+"/"+date[3]+"/"+date[1]+" "+date[4].substr(0,2)+":"+date[4].substr(2,2)+":"+date[4].substr(4,2)+" UTC";
                a.time = new Date(newDate).toISOString();
                return a;
            });
            $scope.tableParams.reload();
        });
    };

    $scope.init = function() {
        $scope.backups = [];
        this.fetchBackups();
    };

    /**For table pagination**/
    $scope.tableParams = new ngTableParams({
        page: 1,
        count: appSettings.tableSettings.count,
        sorting: {
            "name": "asc"
        }
    }, {
        counts:[],
        getData: function($defer, params) {
            appServices.tablePagination($defer, $filter, params, $scope.backups, $scope.searchKeyword);
        }
    });

    $scope.toggleAnimation = function() {
        $scope.animationsEnabled = !$scope.animationsEnabled;
    };

    $scope.$watch("searchKeyword", function () {
        $scope.tableParams.reload();
        $scope.tableParams.page(1);
    });

    $scope.init();

});
angular.module('PoapServer').controller('CreateBackupCtrl',function($scope, $modalInstance, appServices, appSettings, dataToModal) {
    $scope.init = function() {
        appServices.doAPIRequest(appSettings.appAPI.backup.add, null, null).then(function(data) {
            $modalInstance.close();
        });
    };

    $scope.init();
});