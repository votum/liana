# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/16/15

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField


class Article(TimeStampedModel):
    title = models.CharField(max_length=500)
    shop = models.CharField(max_length=500)
    shop_url = models.URLField(max_length=1000)
    shop_id = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.CharField(max_length=200, blank=True, null=True)
    availability = models.CharField(max_length=200, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/articles/%s/' % self.pk
