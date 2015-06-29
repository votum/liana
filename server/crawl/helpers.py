# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/18/15
import resource
import re
import sys
import urlparse

class ShopConfig(object):
    def __init__(self, config):
        self.__config = config
        self.update_current = False
        self.start_url = config.get('startUrl')
        url = urlparse.urlsplit(self.start_url)
        self.base_url = url.scheme + '://' + url.netloc
        self.shop_name = config.get('shopName', url.netloc)

        self.field_match = config['fieldMatch']
        self.leaf_only = config.get('leafOnly', False)

        self.generic_tag = config.get('genericTag')
        self.suppress_ua = config.get('suppressUA')

        if config.get('ignoreUrlRegexp'):
            self.ignore_url_regexp = re.compile(config.get('ignoreUrlRegexp'))
        else:
            self.ignore_url_regexp = None

        if config.get('articleUrlRegexp'):
            self.article_url_regexp = re.compile(config.get('articleUrlRegexp'))
        else:
            self.article_url_regexp = None

        self.link_selector = config.get('linkSelector', 'a')

    def get_original(self):
        return self.__config


def log(*texts):
    sys.stdout.write("%s\n" % ' '.join(['%s' % t for t in texts]))

def get_mem():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1000 * 1000)

def log_mem():
    log('Memory', get_mem())


