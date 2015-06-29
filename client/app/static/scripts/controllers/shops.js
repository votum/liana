'use strict';

angular.module('clientApp')
    .controller('ShopsCtrl', ['$scope', '$http', function ($scope, $http) {


        var updateShops = function () {
            $http({method: 'GET', url: '/api/shops/'}).
                success(function (data) {
                    $scope.shops = data;
                });
        };

        updateShops();

    }]);
