# -*- coding: utf-8 -*-
from api.views import ArticleViewSet, SearchViewSet, ShopViewSet, IndexStatusViewSet, TagCloudViewSet
from django.conf.urls import patterns, include, url
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'articles', ArticleViewSet)
router.register(r'shops', ShopViewSet, base_name='shops')
router.register(r'crawl/status', IndexStatusViewSet, base_name='crawl_status')
router.register(r'search', SearchViewSet, base_name='search')
router.register(r'tags/cloud', TagCloudViewSet, base_name='tag_cloud')

urlpatterns = patterns('api.views',
                       url(r'^', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       )
