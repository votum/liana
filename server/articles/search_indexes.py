# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/18/15

from articles.models import Article
from haystack import indexes
from django.utils import six



class TagField(indexes.CharField):
    field_type = 'string'

    def prepare(self, obj):
        return self.convert(super(TagField, self).prepare(obj))

    def convert(self, value):
        if value is None:
            return None

        if isinstance(value, list):
            value = ', '.join(value)
        return six.text_type(value)

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    shop = indexes.CharField(model_attr='shop')
    shop_url = indexes.CharField(model_attr='shop_url')
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField(model_attr='description', null=True)
    tags = TagField(model_attr='tags', null=True)
    price = indexes.CharField(model_attr='price', null=True)
    image = indexes.CharField(model_attr='image', null=True)

    def get_model(self):
        return Article
