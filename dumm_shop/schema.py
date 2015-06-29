# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/19/15
import urllib
import microdata
import pprint

pp = pprint.PrettyPrinter(indent=4)

def parse_content_microdata(parse_url):
        # https://developers.google.com/structured-data/testing-tool/
        # not working with http://www.bonprix.de/produkt/maxi-jerseykleid-dunkelblau-bedruckt-958483/
        # which is good microformat according to google

        print parse_url

        items = microdata.get_items(urllib.urlopen(parse_url))
        data = [i.json_dict() for i in items]

        pp.pprint(data)
        return data


parse_content_microdata('https://www.otto.de/p/lotus-style-edelstahlarmband-mit-pu-marc-marquez-ls1681-2-2-485530997/#variationId=485531480')
