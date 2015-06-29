# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/16/15
import threading
import traceback
from articles.models import Article
from crawl.helpers import log, ShopConfig
from crawl.models import IndexStatus
from crawl.parser import Parser
from Queue import Queue
import time
import gc

SPIDER_COUNT = 35


class Spider(threading.Thread):
    def __init__(self, queue, config, save_data_func, add_urls_func):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True

        self.save_data_func = save_data_func
        self.add_urls_func = add_urls_func

        self.parser = Parser(config)
        self.start()

    def run(self):
        while True:
            url = self.queue.get()

            try:
                data, urls = self.parser.parse(url)

                if data:
                    self.save_data_func(data)

                if urls:
                    self.add_urls_func(urls)

            except Exception, e:
                log('ERROR', url, e, '\n', traceback.format_exc())

            gc.collect()
            self.queue.task_done()


class SpiderPool(object):
    def __init__(self, config_dict, spider_count=SPIDER_COUNT):

        self.config = ShopConfig(config_dict)
        self.add_urls_lock = threading.Lock()
        self.update_lock = threading.Lock()

        self.crawled = []
        self.queue = Queue()

        self.articles_found = 0
        self.spider_count = spider_count

        for i in range(self.spider_count):
            Spider(self.queue, self.config, self.save_data, self.add_urls)

    def wait_completion(self):
        self.queue.join()

    def save_data(self, data):

        if self.config.update_current:
            log('update', data['shop_url'])
            with self.update_lock:
                Article.objects.filter(shop=data['shop_url']).update(**data)
        else:
            log('save', data['shop_url'])
            Article.objects.bulk_create([Article(**data)])
        self.articles_found += 1

        self.status.data = self.get_status()
        self.status.save()

    def add_urls(self, urls):
        with self.add_urls_lock:
            for url in urls:
                if url in self.crawled:
                    continue
                self.crawled.append(url)
                self.queue.put(url)

    def clean_current(self):
        Article.objects.filter(shop=self.get_name()).delete()

    def skip_current(self):
        self.crawled.extend(Article.objects.filter(shop=self.get_name()).values_list('shop_url', flat=True))

    def update_current(self):
        self.config.leaf_only = True
        self.config.update_current = True
        self.crawled.append(self.config.start_url)
        self.add_urls(Article.objects.filter(shop=self.get_name()).values_list('shop_url', flat=True))

    def run(self):
        self.start_time = time.time()
        self.status = IndexStatus(shop=self.get_name(), data=self.get_status(), config=self.config.get_original())
        self.status.save()

        log('start', self.get_name())

        self.add_urls([self.config.start_url])

        self.wait_completion()

        self.status.data = self.get_status()
        log('end crawling', self.get_name(), ' - ', ', '.join(['%s: %s' % (d[0], d[1]) for d in self.status.data.items()]))

        self.status.finished = True
        self.status.save()

    def get_crawled_count(self):
        return len(self.crawled)

    def get_name(self):
        return self.config.shop_name

    def get_status(self):
        time_consumed = time.time() - self.start_time
        status = {
            'articles_found': self.articles_found,
            'sites': len(self.crawled),
            'time_consumed': "%.2f secs" % time_consumed,
            'spider_count': self.spider_count,
            'queue_size': self.queue.qsize(),
            'articles/sec': self.articles_found / time_consumed
        }

        if self.config.update_current:
            status['update_only'] = True

        return status
