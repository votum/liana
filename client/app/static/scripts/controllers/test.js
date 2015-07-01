'use strict';

angular.module('clientApp')
    .controller('TestCtrl', ['$scope', '$http', function ($scope, $http) {
        var start,
            baseUrl,
            clear = function () {
                $scope.numberOfrequets = 0;
                $scope.numberOfObjects = 0;
                $scope.objectsPerSecond = 0;
                $scope.currentUrl = '';
                start = new Date().getTime();
                $scope.timeUsed = 0;
            };

        clear();
        $scope.inProgress = false;

        var startCallApi = function (url) {
            clear();
            var pageSize = document.getElementById('page-size').value;
            if (pageSize) {
                url = url + '?page_size=' + pageSize;
            }
            $scope.inProgress = true;
            // start api call recursive
            callApi(url);
        };

        var callApi = function (url) {
            $scope.numberOfrequets++;
            $scope.currentUrl = url;
            $http({method: 'GET', url: url}).
                success(function (data) {

                    $scope.article = data;
                    $scope.numberOfObjects = $scope.numberOfObjects + data.results.length;
                    var end = new Date().getTime();
                    $scope.timeUsed = (end - start) / 1000.0;

                    if ($scope.timeUsed) {
                        $scope.objectsPerSecond = ($scope.numberOfObjects / $scope.timeUsed).toFixed(2);
                    }

                    if (data.next) {

                        // handle standard api call
                        callApi(data.next);
                    } else if (data.scroll_id) {

                        // handle scroll api call
                        callApi(baseUrl + '?scroll_id=' + data.scroll_id);
                    } else {

                        // finished
                        $scope.inProgress = false;
                    }


                }).error(function (data) {
                    if (data) {
                        window.alert(data);
                        $scope.inProgress = false;
                    }
                });
        };

        $scope.start = function () {
            startCallApi('/api/articles/');
        };

        $scope.startScroll = function () {
            baseUrl = '/api/articles/scroll/';
            startCallApi(baseUrl);
        };


    }]);
