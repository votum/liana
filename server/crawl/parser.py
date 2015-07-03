# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/18/15
import StringIO
import gzip
from django.utils.encoding import smart_str
import re
import urllib
import urllib2
from bs4 import BeautifulSoup
from crawl.helpers import log, log_mem
import urlparse
from django.template.defaultfilters import removetags
import microdata

LOC_RE = re.compile('<loc.*?>(.+?)</loc>')


class Parser(object):
    def __init__(self, config):
        self.config = config
        self.opener = urllib2.build_opener()

        if not config.suppress_ua:
            self.opener.addheaders = [
                ('User-agent', 'Mozilla/5.0 (compatible; lianabot/0.5; +http://www.lianakit.com/')]

    def parse(self, url):

        url = smart_str(url)

        if '.xml' in url:
            return self.parse_content_sitemap(url)
        elif self.config.field_match == 'microdata':
            return self.parse_content_microdata(url)

        return self.parse_content_html(url)

    def is_valid_href(self, href):
        if href.startswith('http://') or href.startswith('https://'):

            href = href.replace('https:', '').replace('http:', '')
            base_url = self.config.base_url.replace('https:', '').replace('http:', '')

            if not href.startswith(base_url):
                return False

        if href == '#':
            return False

        if self.config.ignore_url_regexp and self.config.ignore_url_regexp.findall(href):
            return False

        return True

    def sanitize_url(self, href, base=None):
        if base is None:
            base = self.config.base_url

        if href[0:4] == 'http':
            return href

        return urlparse.urljoin(base, href).lower()

    def valid_tag(self, tag_text):
        t = Parser.purify_text(tag_text.lower())
        if len(t) < 3:
            return False

        return not t in ['...', 'home', 'shop', 'startseite', 'page', 'all']

    def parse_content_sitemap(self, parse_url):
        log('start sitemap', parse_url)
        data_string = self.opener.open(parse_url).read()

        if parse_url.endswith('.gz'):
            compressedFile = StringIO.StringIO()
            compressedFile.write(data_string)

            compressedFile.seek(0)
            xml = gzip.GzipFile(fileobj=compressedFile, mode='rb')
            data_string = xml.read()
            del xml

        found = LOC_RE.findall(data_string)

        urls = []
        for loc in found:
            href = self.sanitize_url(loc)
            if self.is_valid_href(href):
                urls.append(href)

        log('end sitemap', parse_url, len(urls))

        return None, urls

    def parse_content_microdata(self, parse_url):
        # https://developers.google.com/structured-data/testing-tool/
        # not working with http://www.bonprix.de/produkt/maxi-jerseykleid-dunkelblau-bedruckt-958483/
        # which is good microformat according to google

        log('parse', parse_url)

        items = microdata.get_items(urllib.urlopen(parse_url))

        data = [i.json() for i in items]
        urls = []

        return data, urls

    def parse_content_html(self, parse_url):
        log('parse', parse_url)

        urls = []
        data = {}

        data_string = self.opener.open(parse_url).read()
        soup = BeautifulSoup(data_string, "lxml")

        if not self.config.article_url_regexp or self.config.article_url_regexp.findall(parse_url):

            data = {'shop_url': parse_url, 'shop': self.config.shop_name}

            for k, v in self.config.field_match.items():

                v, use_html = Parser.use_pseudo(v, '::html')
                v, use_href = Parser.use_pseudo(v, '::href')
                v, use_all = Parser.use_pseudo(v, '::all')
                v, custom_attr = Parser.use_pseudo_with_arg(v, '::attr')

                def get_attr(tag, attr):
                    return tag.attrs.get(custom_attr if custom_attr else attr, '')

                hits = soup.select(v)
                if len(hits):
                    tag = hits[0]

                    if tag.name == 'img':
                        data[k] = urlparse.urljoin(self.config.base_url, get_attr(tag, 'src'))
                    elif use_href:
                        data[k] = get_attr(tag, 'href')
                    elif use_html:
                        data[k] = removetags(Parser.purify_text('%s' % tag), 'img script style span br')
                    elif use_all:
                        data[k] = [Parser.purify_text(h.text.replace(',', ' ')) for h in hits if
                                   self.valid_tag(h.text)]
                        if k == 'tags' and self.config.generic_tag:
                            data[k].append(self.config.generic_tag)
                    else:
                        text = get_attr(tag, 'content')
                        if not text:
                            text = tag.text
                        if not text:
                            text = tag.attrs.get('href', '')

                        if k == 'image':
                            text = urlparse.urljoin(self.config.base_url, text)

                        data[k] = Parser.purify_text(text)

            if not data.has_key('title') or not data.has_key('description') or not data.has_key('price'):
                data = {}

        if not self.config.leaf_only:

            # respect <base href="http://www.base.com/shop/"/> head tag
            sanitize_url_kwargs = {}
            base = soup.select('base')
            if len(base):
                sanitize_url_kwargs['base'] = base[0].attrs.get('href')

            for tag in soup.select(self.config.link_selector):
                href = tag.attrs.get('href')
                if href and self.is_valid_href(href):
                    href = self.sanitize_url(href, **sanitize_url_kwargs)
                    urls.append(href)

        soup.decompose()
        del soup
        del data_string

        return data, urls

    @staticmethod
    def use_pseudo(value, pseudo_class):
        if value.endswith(pseudo_class):
            return value.replace(pseudo_class, ''), True

        return value, False

    @staticmethod
    def use_pseudo_with_arg(value, pseudo_class):
        parts = value.split(pseudo_class + '/')
        if len(parts) == 1:
            return value, None

        return parts[0], parts[1]

    @staticmethod
    def purify_text(text):
        return ' '.join(text.replace('\n', ' ').replace('\r', ' ').replace('<', ' <').replace('  ', ' ').strip().split())
