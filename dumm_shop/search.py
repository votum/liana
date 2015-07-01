# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/19/15
import os
from elasticsearch import Elasticsearch
import sys


def print_res(data):
    hits = data['hits']['hits']

    print("Got %d Hits:" % data['hits']['total'])
    print("Got %d Hits:" % len(hits))
    print("Got %d" % sys.getsizeof(hits))
    print res.keys()

    if len(hits):
        print 'First elem %s ' % hits[0]['_source']


ES_SSL_URL = os.environ.get('ELASTIC_SSL_URL')
es = Elasticsearch([ES_SSL_URL])

body = {
    "query": {
        "match_all": {}
    },
    "size": 10000
}

res = es.search(index="liana_documents",
                scroll="1h",
                search_type="scan",
                body=body)

scroll_id = res['_scroll_id']
print scroll_id


for r in range(1,3):
    res = es.scroll(scroll_id=scroll_id, scroll="1h")

    print res['_scroll_id']
    print_res(res)

