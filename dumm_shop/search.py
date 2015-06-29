# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/19/15
from elasticsearch import Elasticsearch


es = Elasticsearch(['https://paas:2636041f3de3037424261e53f3eac4a7@kili-eu-west-1.searchly.com'])

body = {
    "query": {
        "fuzzy": {
            "text": "Sonos"
        }
    }}

res = es.search(index="liana_documents",
                body=body)  # res = es.search(index="liana_documents", body={"query": {"match_all": {}}})


print res['hits'].keys()
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    del hit['_source']['description']
    del hit['_source']['text']
    print(hit['_score'], hit['_source'])
