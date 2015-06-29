# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/16/15

from django.db import models
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel


class IndexStatus(TimeStampedModel):
    shop = models.CharField(max_length=500)
    finished = models.BooleanField(default=False)
    data = JSONField(blank=True, null=True)
    config = JSONField(blank=True, null=True)

    def __unicode__(self):
        return self.shop

