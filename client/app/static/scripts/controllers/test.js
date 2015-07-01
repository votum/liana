'use strict';

angular.module('clientApp')
    .controller('TestCtrl', ['$scope', '$http', function ($scope, $http) {
        var start;
        var clear = function () {
            $scope.numberOfrequets = 0;
            $scope.numberOfObjects = 0;
            $scope.currentUrl = '/api/articles/';
            start = new Date().getTime();
            $scope.timeUsed = 0;
        };
        clear();
        $scope.inProgress = false;

        var callApi = function (url) {
            $scope.numberOfrequets++;
            $scope.currentUrl = url;
            $http({method: 'GET', url: url}).
                success(function (data) {

                    $scope.article = data;
                    $scope.numberOfObjects = $scope.numberOfObjects + data.results.length;

                    var end = new Date().getTime();
                    $scope.timeUsed = (end - start) / 1000.0;

                    // check if finished
                    if (data.next) {
                        callApi(data.next);
                    } else {
                        $scope.inProgress = false;
                    }

                }).error(function (data) {
                    window.alert(data);
                });
        };

        // start api call recursive
        $scope.start = function () {
            clear();

            var url = '/api/articles/';
            var pageSize = document.getElementById('page-size').value;

            if (pageSize) {
                url = url + '?page_size=' + pageSize;
                $scope.inProgress = true;
            }

            callApi(url);
        };

    }]);
