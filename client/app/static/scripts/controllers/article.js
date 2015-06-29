'use strict';

angular.module('clientApp')
    .controller('ArticleCtrl', ['$scope', '$http', '$stateParams', function ($scope, $http, $stateParams) {

        $http({method: 'GET', url: '/api/articles/' + $stateParams.articleId + '/'}).
            success(function (data) {
                $scope.article = data;

                $http({
                    method: 'GET',
                    url: '/api/search/more_like_this/?size=4&q=' + encodeURIComponent($scope.article.title) + '&exclude_id=' + $scope.article.id
                }).
                    success(function (data) {
                        $scope.likeArticles = data.results;
                    });

            }).error(function (data) {
                window.alert(data);
            });
    }]);
