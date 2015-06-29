# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/16/15
from articles.models import Article
from django.contrib import admin


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('modified', 'title', 'shop')
    list_filter = ['shop']
    search_fields = ['shop', 'title', 'tags', 'description', 'shop_url', 'image']
