# spiders/quotes.py

import scrapy
import logging
import json
import os
from ..items import StateItem, MuniItem, ParkingCodeItem
from scrapy_playwright.page import PageMethod


class SearchspiderSpider(scrapy.Spider):
    name = 'searchspider'
    allowed_domains = ['library.municode.com']
    start_url = ['https://library.municode.com']

    parking_dir = os.path.join('jsons', 'parking_code.json')
    custom_settings = {
        'FEEDS': {
            parking_dir: {
                'format': 'json',
                'overwrite': True}
        }
    }

    def __init__(self):
        json_dir = os.path.join('jsons', 'municipalities.json')
        with open(json_dir) as data_file:
            self.data = json.load(data_file)

        self.keywords = ['"spaces per"', '"required parking"', '"parking schedule"']
        self.no_url_dir = os.path.join('jsons', 'no_url.json')
        # logging.getLogger('scrapy').setLevel(logging.WARNING)
        logging.getLogger('scrapy-playwright').setLevel(logging.WARNING)

    def start_requests(self):
        # other keywords to try "off-street parking", "1 space"
        print(f"There are {len(self.data)} municipalities")
        for item in self.data:
            # item = {"state": "Arizona", "muni": "Douglas", "url": "https://library.municode.com/az/douglas"}
            # for key in self.keywords, can't send duplicate requests
            print(f"Crawling through {item['state'], item['muni']}")
            yield scrapy.Request(item["url"], callback=self.parse_search,
                                 meta=dict(
                                     playwright=True,
                                     playwright_include_page=True,
                                     playwright_page_methods={"load1": PageMethod('wait_for_timeout', 6000),
                                                              "type": PageMethod('type', selector='div.form-group > input',
                                                                                 text=self.keywords[0]),
                                                              "enter": PageMethod('press',
                                                                                  selector='div.form-group > input',
                                                                                  key='Enter'),
                                                              "load2": PageMethod('wait_for_timeout', 6000)},
                                     errback=self.errback), cb_kwargs=item)
            # stops once it reaches a site that redirects it to a different site like Preston, ID

    async def parse_search(self, response, state, muni, url):
        print(f"\n\n\nIn parse_search for {muni}, {state}:")
        page = response.meta["playwright_page"]
        await page.close()
        # print(page)
        parking_url = response.xpath('//h4/a/@href').get()

        # add a section to check if the first link is the right ones

        parking_code = ParkingCodeItem()
        parking_code['state'] = state
        parking_code['municipal'] = muni
        parking_code['state_url'] = url
        parking_code['parking_code'] = parking_url
        yield parking_code


    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        print('\n\n\nIn errback\n\n\n')
        # need to deal with site redirects like Alpine, Utah

