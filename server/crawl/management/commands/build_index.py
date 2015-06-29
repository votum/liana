# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/21/15
from django.core.management import call_command
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'update search index'

    def handle_noargs(self, **options):
        from crawl.helpers import log
        print log('update index ...')
        call_command('update_index', interactive=False)
        print log('update index finished')
