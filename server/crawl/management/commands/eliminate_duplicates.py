# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/21/15
from django.core.management.base import NoArgsCommand
from django.db.models import Count


class Command(NoArgsCommand):
    help = 'eliminate duplicates.'

    def handle_noargs(self, **options):
        from crawl.helpers import log
        from articles.models import Article

        i = 0
        for d in Article.objects.values('image').annotate(Count('id')).order_by().filter(id__count__gt=1,
                                                                                         image__isnull=False):
            Article.objects.filter(
                id__in=Article.objects.filter(image=d['image']).values_list('id', flat=True)[1:]
            ).delete()

            i += 1
            log(i, 'duplicates found ...')

        log('end', i, 'duplicates found')
