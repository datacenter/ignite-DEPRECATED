(function() {

    'use strict';

    /**
     * @ngdoc overview
     * @name clmServiceRequestApp Config.js
     * @description
     * # ccpServiceRequestApp
     *        $http.get(url, config)
     *        $http.post(url, data, config)
     *        $http.put(url, data, config)
     *        $http.delete(url, data, config)
     */

    angular.module("PoapServer")
        .service('appServices', function($http, $q, $timeout, $log, $rootScope, $location, appSettings, lclStorage) {

            var appServices = this;

            appServices.errors = [];
            appServices.loginError = '';

            appServices.generateSeq = function(page, count, $index) {
                return ((page - 1) * count ) + $index + 1;
            };

            appServices.clearErrors = function() {
                appServices.errors = [];
                $rootScope.errorFlag = false;
            };

            appServices.setInternalAppUI = function($scope) {
                $scope.$parent.bodyClass = "";
                $scope.$parent.isLogin = false;
            };

            appServices.tablePagination = function($defer, $filter, params, data, searchKeyword) {
                    var filteredData = params.filter() ? $filter('filter')(data, searchKeyword) : data;
                    var orderedData = params.sorting() ? $filter('orderBy')(filteredData, params.orderBy()) : filteredData;
                    var paginatedData = orderedData.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    params.total(filteredData.length);

                    if(paginatedData.length > 0) {
                        $defer.resolve(paginatedData);
                    }
                    else {
                        var currentPage = params.page();
                        if(currentPage > 1) {
                            params.page(currentPage - 1);
                        } else {
                            $defer.resolve(paginatedData);
                        }
                    }
            };

            appServices.getUrlParameter = function(sParam) {
                var locationUrl = $location.url();
                if (locationUrl.indexOf('?') != -1) {
                    var sPageURL = locationUrl.split('?');

                    //set the param to the URL so that links can use it
                    appServices.urlParameters = sPageURL[1];

                    var sURLVariables = sPageURL[1].split('&');
                    for (var i = 0; i < sURLVariables.length; i++) {
                        var sParameterName = sURLVariables[i].split('=');
                        if (sParameterName[0] == sParam) {
                            return sParameterName[1];
                        }
                    }
                }
            };

            appServices.generateUniqueName = function(arrayList, name) {

                var cName = name;
                var sName = name.split('_');
                if(!isNaN(sName[sName.length - 1])) {
                    var newName = '';
                    for(var i = 0; i < sName.length - 1; i++) {
                        newName = newName + '_' + sName[i];
                    }

                    cName = newName.substring(1, newName.length);
                }

                if(typeof arrayList != 'undefined') {
                    var counter = 0;
                    var nameNumberArray = [];
                    angular.forEach(arrayList, function(val,key) {
                        if(val.name.indexOf(cName) > -1 ) {
                            var c_name_number = val.name.split('_');
                            if(c_name_number.length > 1) {
                                c_name_number = c_name_number[c_name_number.length - 1];
                                if(!isNaN(c_name_number)) {
                                    nameNumberArray.push(Number(c_name_number));
                                }
                            }
                            counter++;
                        }
                    });

                    /*sort in decending order and get the highest values from it */
                    nameNumberArray.sort(function(a, b){return b-a});

                    if(nameNumberArray.length == 0) {
                        nameNumberArray[0] = 0;
                    }
                    return cName + "_" + (nameNumberArray[0] + 1);
                }
            }

            appServices.getStaticFile = function(settingsPath) {
                var defer = $q.defer();
                var url = appSettings.static.baseURL + settingsPath.url;
                var httpParams = {
                    url: url
                };

                $timeout(function() {
                    $http(httpParams)
                        .success(function(data, status, headers, config) {
                            defer.resolve(data);
                        })
                        .error(function(error, status, headers, config) {
                            if (status >= 400 && status < 600) {
                                return error;
                            } else {
                                $log.debug('Error: Could not fetch data from:\n----------------------------------\n' + httpParams.url);
                            }
                            defer.resolve(error);
                            defer.reject(error);
                        })
                }, 0);

                return defer.promise;
            };


            appServices.doAPIRequest = function(callAPISettings, requestParams, headerParams) {
                var defer = $q.defer();
                var requestMethod = callAPISettings.method;
                var url = appSettings.appAPI.baseURL + callAPISettings.url;



                var httpParams = {
                    method: requestMethod,
                    url: url
                };

                if(typeof requestParams != "undefined" && requestParams != null) {
                    httpParams.data = requestParams;
                }


                if(callAPISettings.auth == "true") {
                    try{
                        var requestHeader = {
                            "Content-Type" : "application/json",
                            "Authorization" : lclStorage.get('userDetails').auth_token
                        };
                    } catch(e) {
                        var errMsg = {
                                msg : {
                                    error_message : "Session Expired! Please login again."
                                }
                            }
                            appServices.errors.push(errMsg)
                            $rootScope.errorFlag = true;
                            $location.path("/");
                            return error;
                    }
                    httpParams.headers = requestHeader;
                }


                if(headerParams!= null && typeof headerParams != 'undefined') {
                    if(headerParams.appendToURL == true) {
                        if(headerParams.noTrailingSlash) {
                            httpParams.url = url + headerParams.value;
                        }
                        else {
                            httpParams.url = url + headerParams.value + "/";
                        }

                    }



                    if(headerParams.fileUpload == true) {
                        if(typeof httpParams.headers != 'undefined') {
                            httpParams.headers["Content-Type"] = undefined;
                        }
                        else {
                            httpParams.headers = {
                                "Content-Type" : undefined,
                            }
                        }

                        //httpParams.headers.transformRequest = angular.identity;

                        var fd = new FormData();
                        fd.append("file", requestParams)

                        httpParams.data = fd;
                        var version_data = { 'new_version':headerParams.new_version };
                        httpParams.data.new_version = headerParams.new_version;

                    }
                }

                console.log('httpParams ===================== ');
                console.log(httpParams);

                $timeout(function() {
                    $http(httpParams)
                        .success(function(data, status, headers, config) {
                            appServices.loginError = '';

                            if(data.status == 'error') {

                                var errMsg = {
                                    msg : data.errorMessage
                                }

                                appServices.errors.push(errMsg)
                                $rootScope.errorFlag = true;
                            }

                            defer.resolve(data);
                        })
                        .error(function(error, status, headers, config) {
                            var errMsg = null;
                            if(status == 401) {
                                if(error.error != undefined){
                                    errMsg = {
                                        msg : {
                                            error_message : error.error
                                        }
                                    }
                                } else if(error.status != undefined){
                                    errMsg = {
                                        msg : {
                                            error_message : error.status
                                        }
                                    }
                                } else if (errMsg == null) {
                                    errMsg = {
                                        msg : {
                                            error_message : "Session Expired! Please login again."
                                        }
                                    }
                                }
                                appServices.errors.push(errMsg);
                                $rootScope.errorFlag = true;
                                $location.path("/");
                                return error;
                            } /*else if(status == 403) {
                                if(typeof error.error_message !="undefined") {
                                    errMsg = {
                                        msg : error.error_message
                                    }
                                } else {
                                    errMsg = {
                                        msg : error
                                    }
                                    if(typeof errMsg.msg.error_message == "undefined") {
                                        errMsg.msg = {};
                                        errMsg.msg.error_message = "Error! Please look into server logs for details.";
                                    }
                                }
                                appServices.errors.push(errMsg);
                                $rootScope.errorFlag = true;
                                $location.path($rootScope.prevLocation);
                                return error;
                            }*/ else if (status >= 400 && status < 600) {
                                
                                if(typeof error.errorMessage !="undefined") {
                                    errMsg = {
                                        msg : error.errorMessage
                                    }
                                    appServices.errors.push(errMsg)
                                }

                                else if(typeof error.non_field_errors != "undefined") {
                                    appServices.loginError = error.non_field_errors[0];
                                    errMsg = {
                                        msg : {
                                            error_message : error.non_field_errors[0]
                                        }
                                    }
                                    appServices.errors.push(errMsg)
                                }
                                else {
                                    errMsg = {
                                        msg : error
                                    }
                                    if(typeof errMsg.msg.error_message == "undefined") {
                                        errMsg.msg = {};
                                        errMsg.msg.error_message = "Error! Please look into server logs for details.";
                                    }
                                    appServices.errors.push(errMsg)
                                }
                                $rootScope.errorFlag = true;
                                if(status == 403 && $rootScope.prevLocation != undefined) {
                                    $location.path(angular.copy($rootScope.prevLocation));
                                    $rootScope.prevLocation = undefined;
                                }
                                return error;
                            } else {
                                $log.debug('Error: Could not fetch data from:\n----------------------------------\n' + httpParams.url);
                            }
                            //defer.resolve(error);
                            defer.reject(error);
                        })
                }, 0);

                return defer.promise;
            }


            appServices.getUtilizationColor = function(val) {
                var color = "";
                angular.forEach(appSettings.threshold, function(value, key) {
                    if(val >= value.range[0] && val <= value.range[1]){
                        color = value.color;
                        return false;
                    }
                })


                return color;
            };


            return appServices;
        })
        .factory('lclStorage', function(store) {
            return store.getNamespacedStore('ccpStore');
        })
}());
