# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/16/15
from crawl.models import IndexStatus
from django.contrib import admin


@admin.register(IndexStatus)
class IndexStatusAdmin(admin.ModelAdmin):
    list_display = ('created',  'shop', 'finished')
    list_filter = ['shop', 'finished']
