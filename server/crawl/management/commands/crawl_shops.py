# -*- coding: utf-8 -*-
#
# Copyright (c) maersu. All rights reserved.
#
# Created on 6/16/15
from optparse import make_option
from crawl.helpers import log
from crawl.spider import SpiderPool, SPIDER_COUNT
from django.core.management import call_command
from django.core.management.base import NoArgsCommand

DUMMY = 'dummy'

# TODO https://github.com/edsu/microdata
RDF_SELECTORS = {
    'title': '[itemprop="name"]',
    'description': '[itemprop="description"]',
    'price': '[itemprop="price"]',
    'image': '[itemprop="image"]',
    'tags': '[itemtype="http://data-vocabulary.org/Breadcrumb"] a span::all',
    'availability': '[itemprop="availability"]',
    'shop_id': '[itemprop="sku"]'
}


def get_rdf_selectors(overwrite=None):
    if overwrite:
        c = RDF_SELECTORS.copy()
        c.update(overwrite)
        return c
    return RDF_SELECTORS


class Command(NoArgsCommand):
    help = 'Crawls some shops'

    option_list = NoArgsCommand.option_list + (
        make_option('-f', '--shop_filter', dest='shop_filter',
                    help='Filters shop config'),
        make_option('-s', '--spider_count', dest='spider_count', default=SPIDER_COUNT,
                    help='spider count'),
        make_option("-d", "--dummy",
                    action="store_true", dest="dummy", default=False,
                    help="Use dummy store"),
        make_option("-c", "--skip_current",
                    action="store_true", dest="keep_current", default=False,
                    help="Use dummy store"),
        make_option("-u", "--update_current",
                    action="store_true", dest="update_current", default=False,
                    help="Use dummy store"),
        make_option("--delete", dest="delete",
                    help="delete given store"),
    )

    def handle_noargs(self, **options):

        delete = options.get('delete')
        if delete:
            from articles.models import Article

            log('delete', Article.objects.filter(shop=delete).count())
            Article.objects.filter(shop=delete).delete()
            return

        if options.get('dummy', False):
            shop_filter = DUMMY
        else:
            shop_filter = options.get('shop_filter', None)

        update_current = options.get('update_current', False)
        keep_current = options.get('keep_current', False)
        spider_count = int(options.get('spider_count'))

        shops_config = {

            'mondovino': {
                'startUrl': 'https://www.mondovino.ch/sitemap/sitemap_de.xml',
                'ignoreUrlRegexp': r'/sortiment|mailto|javascript',
                'leafOnly': True,
                'genericTag': 'Wein',
                'fieldMatch':
                    {
                        'title': '.mod_product_detail__title',
                        'description': '.mod_product_detail__description_text',
                        'price': 'span.mod_product_detail__price_box_price',
                        'image': '.mod_product_detail__product_image noscript img',
                        'tags': 'a[href="#grapes"]::all'
                    }
            },

            'c-and-a': {
                'startUrl': 'http://www.c-and-a.com/ch/de/sitemap/sitemap.xml',
                'ignoreUrlRegexp': r'/information|/service|/corporate|/blog|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/de/de/|.jpg|mailto|javascript|/land/',
                'articleUrlRegexp': r'/ch/de/',
                'fieldMatch':
                    {

                        'title': '#productDetail h1',
                        'description': '#productDetail .list::html',
                        'price': '.price .normal span',
                        'image': '.productImage a::href',
                        'tags': '.breadcrumb a::all'
                    }
            },

            'interdiscount': {
                'startUrl': 'http://www.interdiscount.ch/idshop/index.jsf',
                'ignoreUrlRegexp': r'/idshop/eneCategory/_/detail.jsf|prospect.jsf|/page/|/pages/|jsessionid|FulltextSearch|mailto|javascript|atwork|__HYBRIS__|/land/',
                'articleUrlRegexp': r'/product/',
                'fieldMatch':
                    {
                        'title': '.innercontent .productNameLine h1',
                        'description': '.innercontent .features::html',
                        'price': '.innercontent .productPrice',
                        'image': '.innercontent .largeImage',
                        'availability': '.availabilityIcon',
                        'tags': '.breadcrumb a::all'
                    }
            },

            'microspot': {
                'startUrl': 'http://www.microspot.ch/sitemap_index.xml',
                'leafOnly': True,
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/de/cat-|prospect.jsf|/page/|/pages/|jsessionid|FulltextSearch|mailto|javascript|atwork|__HYBRIS__|selectedLanguage=it|selectedLanguage=fr|printProduct.jsf',
                'fieldMatch':
                    {
                        'title': '.productName h1',
                        'description': '.rf-tab-cnt::html',
                        'price': '.productList_price',
                        'image': '.mainProductPicture img',
                        'availability': '.deliveryCheckImage',
                        'tags': '.breadcrumb a::all'
                    }
            },

            'galaxus': {
                'startUrl': 'http://www.microspot.ch/sitemap.xml.gz',
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/brand/|/producttype/',

                'leafOnly': True,
                'fieldMatch': get_rdf_selectors()
            },

            'oswald': {
                'startUrl': 'http://www.oswald.ch/xmlsitemaps/ch_de/sitemap.xml',
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/rezepte/',
                'articleUrlRegexp': r'/de/',
                'linkSelector': '.category-view a',

                'fieldMatch': {
                    'title': '.product-name h1',
                    'description': '#marketing-text',
                    'price': '.regular-price',
                    'image': '.product-image img',
                    'availability': '.deliveryCheckImage',
                    'tags': '[itemtype="http://data-vocabulary.org/Breadcrumb"] a span::all'
                }

            },

            'globus': {
                'startUrl': 'https://www.globus.ch/sitemap.xml',
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|sitemap-globus-fr',

                'leafOnly': True,
                'fieldMatch': {
                    'title': '[itemprop="name"]',
                    'description': '[itemprop="description"]',
                    'price': '[itemprop="price"]',
                    'image': 'img.js_pdimage',
                    'tags': '[itemprop="category"] a::all',
                    'availability': '[itemprop="availability"]',
                }

            },

            'bonprix': {
                'startUrl': 'http://www.bonprix.de/sitemap.xml',
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|video.xml|editorial.xml',

                'leafOnly': True,
                'fieldMatch': {
                    'title': '.product-name',
                    'description': '#product-info',
                    'price': '[itemtype="http://schema.org/Product"] [itemprop="price"]',
                    'image': '#productimage::attr/data-main-image',
                    'tags': '[itemtype="http://data-vocabulary.org/Breadcrumb"] a::all',
                    'availability': '[itemtype="http://schema.org/Product"] [itemprop="availability"]',
                }
            },

            'zalando': {
                'startUrl': 'https://www.zalando.de/sitemap.xml',
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/alle/',
                'linkSelector': 'a.catalogArticlesList_productBox',

                'fieldMatch': {
                    'title': '[itemprop="name"]',
                    'description': '#productDetails .content',
                    'price': '.price',
                    'image': '.articleMedia_imagePlaceholder',
                    'tags': '.breadcrumbs_link::all',
                    'availability': '[itemprop="availability"]',
                    'shop_id': '[itemprop="identifier"]'

                }

            },

            'impo': {
                'startUrl': 'http://www.impo.ch/images/sitemap/sitemap_de.xml',
                'ignoreUrlRegexp': r'/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/addToBasket/|/de/cat-|prospect.jsf|/page/|/pages/|jsessionid|FulltextSearch|mailto|javascript|atwork|__HYBRIS__|selectedLanguage=it|selectedLanguage=fr|printProduct.jsf',
                'linkSelector': '.main-center-catalog a',

                'fieldMatch': {
                    'title': '.text-overview-title',
                    'description': '.text-overview-desc',
                    'price': '#productPrice',
                    'image': '#product-pic-variants',
                    'tags': '.breadcrumb-item a::all',
                    'shop_id': '#zobjectid'

                }
            },

            'ochsner': {
                'startUrl': 'http://shop.ochsner-sport.ch/CH/de/shop/sitemap.xml',
                'ignoreUrlRegexp': r'sport.ch#|sport.ch/#|/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/addToBasket/|/de/cat-|prospect.jsf|/page/|/pages/|FulltextSearch|mailto|javascript|atwork|__HYBRIS__|selectedLanguage=it|selectedLanguage=fr|printProduct.jsf',
                'linkSelector': '.thumbname a',
                'articleUrlRegexp': r'/CH/de/shop/',
                'fieldMatch': {
                    'title': '#m_product_facts_name',
                    'description': '.m_product_config .tabContent::html',
                    'price': '#m_product_facts_price',
                    'image': '.img-zoom img',
                    'tags': '#ariadne a::all',
                    'shop_id': '#product.details.product.code'

                }
            },

            'bauundhobby': {
                'startUrl': 'http://www.bauundhobby.ch/sitemap/sitemap_de.xml',
                'ignoreUrlRegexp': r't.ch#|/bauho/|/coop/|.ch/#|/en/|/fr/|/it/|/es/|/nl/|/pl/|/be/|/at/|/addToBasket/|/de/cat-|prospect.jsf|/page/|/pages/|FulltextSearch|mailto|javascript|atwork|__HYBRIS__|selectedLanguage=it|selectedLanguage=fr|printProduct.jsf',
                'linkSelector': '#content-container .product-link',
                'fieldMatch': {
                    'title': '.product-detail-information h1',
                    'description': '.product-details::html',
                    'price': '[itemprop="price"]',
                    'image': '[itemprop="image"]',
                    'availability': '.btn-shopping-cart .btn-text',
                    'tags': '.breadcrumb a::all',

                }
            },

            'chain': {
                'startUrl': 'http://www.chainreactioncycles.com/products-sitemap-index.xml.gz',
                'leafOnly': True,
                'suppressUA': True,
                'generic_tag': 'Bike',
                'fieldMatch':
                    {
                        'title': '.product_title',
                        'description': '.short_desc::html',
                        'price': '#crc_product_rp',
                        'image': '#s7_zoomviewer_staticImage',
                        'availability': '.inventory',
                        'tags': '.breadcrumb a::all'
                    }
            },

            'rei': {
                'startUrl': 'http://www.rei.com/sitemap.xml',
                'ignoreUrlRegexp': r'/smartwool/|/stores/|/b/',
                'articleUrlRegexp': r'/product/',
                'leafOnly': True,
                'fieldMatch': get_rdf_selectors({'tags': '.breadcrumb .itemTitle::all'})
            },

            'otto': {
                'startUrl': 'https://www.otto.de/product/sitemap_index.xml',
                'leafOnly': True,
                'fieldMatch': get_rdf_selectors({})
            },

            DUMMY: {
                'startUrl': 'http://localhost:8888/',
                'genericTag': 'Dummy',
                'fieldMatch':
                    {
                        'title': '.title',
                        'description': '.description::html',
                        'price': '.price',
                        'tags': '.tag::all',
                        'image': 'img',
                    }
            }
        }

        if not shop_filter:
            shop_filter = ','.join([k for k in shops_config.keys() if k != DUMMY])

        for name, config in shops_config.items():

            if name in shop_filter:
                c = SpiderPool(config, spider_count)
                if update_current:
                    c.update_current()
                elif keep_current:
                    c.skip_current()
                else:
                    c.clean_current()

                c.run()
