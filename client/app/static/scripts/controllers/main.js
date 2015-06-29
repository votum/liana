/*global ga */
'use strict';

/**
 * @ngdoc function
 * @name clientApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the clientApp
 */
angular.module('clientApp')
    .controller('MainCtrl', ['$scope', '$http', '$location', '$interval', '$stateParams', function ($scope, $http, $location, $interval, $stateParams) {

        $scope.btnText = 'Search';
        $scope.shop_count = 15;

        var i = 1,
            countUpCounts = function () {
                $scope.aricles_count = $scope.aricles_count + 1;
                i += 1;
                if (i > countUps) {
                    $interval.cancel(stop);
                }
            },
            countUps = 1000,
            stop = $interval(
                countUpCounts,
                200
            );

        $scope.aricles_count = 686764 - countUps;


        $http({method: 'GET', url: '/api/tags/cloud/'}).
            success(function (data) {
                if (data.tagcloud) {
                    $scope.tagCloud = data.tagcloud.terms;
                }
            });

        $scope.updateRandom = function () {
            $scope.onLoad = true;
            $http({method: 'GET', url: '/api/articles/random/?count=12'}).
                success(function (data) {
                    $scope.randomArticles = data.articles;
                    $scope.onLoad = false;
                }).
                error(function () {
                    $scope.onLoad = false;
                });
        };



        $scope.search = function (query) {

            var q = !query ? document.getElementById('search').value : query;
            if ((q) && q.length > 1) {

                ga('send', 'event', 'search', 'q');

                document.getElementById('search').value = q;
                $scope.onLoad = true;
                $scope.btnText = 'Search ...';

                $http({method: 'GET', url: '/api/search/?q=' + q}).
                    success(function (data) {
                        $scope.searchResult = data;
                        $scope.btnText = 'Search';
                        $scope.onLoad = false;
                    }).
                    error(function (data) {
                        window.alert(data);
                        $scope.btnText = 'Search';
                        $scope.onLoad = false;
                    });
            }
        };

        var q = $stateParams.q;
        if (q) {
            $scope.search(q);
        } else {
            $scope.updateRandom();
        }
    }]);


angular.module('clientApp')
    .filter('trust', ['$sce',
        function ($sce) {
            return function (value) {
                // Defaults to treating trusted text as `html`
                return $sce.trustAsHtml(value);
            };
        }
    ])
;