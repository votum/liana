# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/20/15
import base64
import urlparse
from articles.models import Article
from django.conf import settings
from haystack.backends import SQ
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from elasticsearch import Elasticsearch
import json
import urllib2


class SearchBackend(object):
    @staticmethod
    def search(query, max_queries):
        if not query or len(query) < 2:
            return {}, 0

        if settings.ES_SSL_URL:
            return SearchBackend.fuzzy_elastic_search(query, max_queries)
        else:
            return SearchBackend.simple_search(query, max_queries)

    @staticmethod
    def es_search(**kwars):
        if settings.ES_SSL_URL:
            es = Elasticsearch([settings.ES_SSL_URL])
            kwars['index'] = settings.HAYSTACK_CONNECTIONS.get('default', {}).get('INDEX_NAME', 'liana_documents')
            kwars['request_timeout'] = 60
            return es.search(**kwars)

        return {}

    @staticmethod
    def search_stats():
        if settings.ES_SSL_URL:
            index = settings.HAYSTACK_CONNECTIONS.get('default', {}).get('INDEX_NAME', 'liana_documents')

            es = urlparse.urlparse(settings.ES_SSL_URL)

            url = es.scheme + '://' + es.hostname + ':' + str(443)
            url = urlparse.urljoin(url, '/_status')

            request = urllib2.Request(url)

            base64string = base64.encodestring('%s:%s' % (es.username, es.password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

            data = json.load(urllib2.urlopen(request))
            return data["indices"][index]
        return {}

    @staticmethod
    def get_results_from_search(body, max_queries):
        res = SearchBackend.es_search(body=body, size=max_queries)

        if not res:
            return {}, 0

        results = []
        for hit in res['hits']['hits']:
            source = hit['_source']
            source['id'] = int(source['django_id'])
            del source['django_id']
            del source['django_ct']

            if source.get('tags'):
                source['tags'] = source['tags'].split(', ')
            results.append(source)

        return results[:settings.MAX_QUERIES], res['hits']['total']

    @staticmethod
    def random(max_queries):
        if settings.ES_SSL_URL:
            body = {
                "query": {
                    "function_score": {
                        "query": {"match_all": {}},
                        "random_score": {}
                    }
                }
            }

            hits, count = SearchBackend.get_results_from_search(body, max_queries)
            return hits, max_queries

        from api.views import ArticleSerializer

        a = Article.objects.filter(image__isnull=False).order_by('?')[:max_queries]
        serializer = ArticleSerializer(a, many=True)

        return serializer.data, len(a)

    @staticmethod
    def get_article(django_id):
        if settings.ES_SSL_URL:
            body = {
                "query": {
                    "term": {
                        "django_id": django_id
                    }
                }
            }

            hits, count = SearchBackend.get_results_from_search(body, 1)
            if len(hits) > 0:
                return hits[0]
            return hits

        from api.views import ArticleSerializer

        a = Article.objects.get(pk=django_id)
        serializer = ArticleSerializer(a)

        return serializer.data

    @staticmethod
    def fuzzy_elastic_search(query, max_queries):
        body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "text": {
                                    "query": query,
                                    "fuzziness": "AUTO",
                                    "boost": 0.7
                                }
                            }
                        },
                        {
                            "match": {
                                "title": {
                                    "query": query,
                                    "fuzziness": "AUTO",
                                    "boost": 1
                                }
                            }
                        },
                        {
                            "match":
                                {
                                    "title": {
                                        "query": query,
                                        "boost": 1.7
                                    }
                                }
                        },
                        {
                            "match":
                                {
                                    "description": {
                                        "query": query,
                                        "boost": 1.4
                                    }
                                }
                        },
                        {
                            "match":
                                {
                                    "tags": {
                                        "query": query,
                                        "boost": 1.2
                                    }
                                }
                        },
                        {
                            "match":
                                {
                                    "shop": {
                                        "query": query,
                                        "boost": 1
                                    }
                                }
                        }
                    ]
                }
            }
        }

        return SearchBackend.get_results_from_search(body, max_queries)

    @staticmethod
    def more_like_this(query, exclude_id, max_queries):
        body = {
            "query": {
                "fuzzy_like_this": {
                    "fields": [
                        "title"
                    ],
                    "like_text": query,
                    "max_query_terms": max_queries
                }
            }
        }

        if exclude_id:
            body['filter'] = {
                "not": {
                    "term": {
                        "django_id": exclude_id
                    }
                }
            }

        return SearchBackend.get_results_from_search(body, max_queries)

    @staticmethod
    def simple_search(query, max_queries):
        sqs = SearchQuerySet().filter(
            SQ(content=AutoQuery(query)) | SQ(title=AutoQuery(query)) | SQ(description=AutoQuery(query)))[:max_queries]

        results = [{'title': r.title,
                    'id': r.object.id,
                    'description': r.description,
                    'tags': r.tags,
                    'price': r.price,
                    'shop': r.shop,
                    'image': r.image
                    }
                   for r in sqs]

        return results, len(results)

    @staticmethod
    def tag_search(size):

        if size < 1 or not settings.ES_SSL_URL:
            return {}

        body = {
            "query": {
                "match_all": {}
            },

            "facets": {
                "tagcloud": {
                    "terms": {"field": "tags", "size": size + 5}
                }
            }
        }

        res = SearchBackend.es_search(body=body, search_type='count')
        result = res['facets']
        result['tagcloud']['terms'] = [t for t in result['tagcloud']['terms'] if len(t['term']) > 3][:size]

        return result
