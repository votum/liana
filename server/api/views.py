from api.pagination import LargeResultsSetPagination
from articles.models import Article
from articles.search_backend import SearchBackend
from crawl.models import IndexStatus
from django.conf import settings
from django.db.models import Count
from rest_framework import serializers, viewsets
from rest_framework.decorators import list_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ShopViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(
            Article.objects.order_by('-article_count').values('shop').annotate(article_count=Count('shop'))
        )


class SearchViewSet(viewsets.ViewSet):
    """
    *usage:*

        /api/search/?q=term


    *actions:*

    get elasticsearch status with

        /api/search/status/

    get 'like this with'

        /api/search/more_like_this/?q=term&size=4&exclude_id=12

    """

    def list(self, request):
        query = request.GET.get('q', '')
        size = request.GET.get('size', settings.MAX_QUERIES)
        results, count = SearchBackend.search(query, size)

        return Response({'query': query, 'results': results, 'count': count})

    @list_route()
    def status(self, request):
        return Response(SearchBackend.search_stats())

    @list_route()
    def more_like_this(self, request):
        query = request.GET.get('q', '')
        exclude_id = request.GET.get('exclude_id')
        size = int(request.GET.get('size', settings.MAX_QUERIES))

        results, count = SearchBackend.more_like_this(query, exclude_id, size)
        return Response({'query': query, 'results': results, 'count': count})


class TagCloudViewSet(viewsets.ViewSet):
    def list(self, request):
        size = request.GET.get('size', 20)

        tags = SearchBackend.tag_search(size)
        tags['size'] = size

        return Response(tags)


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article


class ArticleSerializerList(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'url', 'title', 'shop')


class ArticleViewSet(viewsets.ModelViewSet):
    """

    param page_size (default=1000, max=10'000)

        /api/articles/?page_size=100

    **actions:**

    get random selection with

        /api/articles/random/?count=4

    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def retrieve(self, request, pk=None):
        return Response(SearchBackend.get_article(pk))

    @list_route()
    def random(self, request):
        data, count = SearchBackend.random(request.GET.get('count', 3))
        return Response({'count': count, 'articles': data})


class JSONSerializerField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class IndexStatusSerializer(serializers.ModelSerializer):
    data = JSONSerializerField()
    config = JSONSerializerField()

    class Meta:
        model = IndexStatus
        fields = ('id', 'created', 'shop', 'data', 'config', 'finished')


class IndexStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndexStatus.objects.all()
    serializer_class = IndexStatusSerializer
