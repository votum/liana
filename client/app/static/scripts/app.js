'use strict';

/**
 * @ngdoc overview
 * @name clientApp
 * @description
 * # clientApp
 *
 * Main module of the application.
 */

angular
    .module('clientApp', [
        'ui.router',
        'restangular',
        'afkl.lazyImage'
    ])
    .config(function ($locationProvider, $urlRouterProvider, $stateProvider, $httpProvider) {
        $locationProvider.html5Mode(true);
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';

        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('home', {
                url: '/:q',
                controller: 'MainCtrl',
                templateUrl: 'static/views/main.html'
            })
            .state('article', {
                url: '/articles/:articleId/',
                templateUrl: 'static/views/article.html',
                controller: 'ArticleCtrl'
            })
            .state('shops', {
                url: '/shops/',
                templateUrl: 'static/views/shops.html',
                controller: 'ShopsCtrl'
            });

    }).run(['$rootScope', '$state', function ($rootScope, $state) {
        $rootScope.openLink = function (href, $event) {
            if ($event) {
                $event.preventDefault();
                $event.stopPropagation();
            }
            window.location.href = href;
        };

        $rootScope.searchClickTerm = function (term, $event) {
            if ($event) {
                $event.preventDefault();
                $event.stopPropagation();
            }
            $state.go('home', {q: term});
        };

        $rootScope.searchClick = function ($event) {
            if ($event) {
                $event.preventDefault();
                $event.stopPropagation();
            }

            var q = document.getElementById('search').value;
            if ((q) && q.length > 1) {
                $state.go('home', {q: q});
            }
        };
    }]);

