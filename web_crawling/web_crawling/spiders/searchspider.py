# spiders/searchspider.py

import scrapy
import logging
import json
import os
from ..items import ParkingCodeItem
from scrapy_playwright.page import PageMethod


class SearchspiderSpider(scrapy.Spider):
    """ Uses the search function in Municode to find urls to parking tables
    Requires .json that lists municipalities and the Municode URL (ex. municipalities.json in the jsons folder)
    This can be generated with the munispider
    """
    name = 'searchspider'
    allowed_domains = ['library.municode.com']
    start_url = ['https://library.municode.com']

    # output directory/file
    parking_dir = os.path.join('jsons', 'parking_code.json')

    # makes sure spider outputs to designated directory and overwrites
    custom_settings = {
        'FEEDS': {
            parking_dir: {
                'format': 'json',
                'overwrite': True}
        }
    }

    def __init__(self):
        """ Initializes parameters
            - Sets what keywords to search for (order matters)
            - Loads .json with municipality information

        """
        json_dir = os.path.join('jsons', 'municipalities.json')
        with open(json_dir) as data_file:
            self.data = json.load(data_file)

        self.keywords = ['"spaces per"', '"required parking"', '"parking schedule"']
        self.no_url_dir = os.path.join('jsons', 'no_url.json')

        # use if logs are cluttering command line
        # logging.getLogger('scrapy').setLevel(logging.WARNING)
        logging.getLogger('scrapy-playwright').setLevel(logging.WARNING)

    def start_requests(self):
        """ Loads muncipality page and searches keyword.
            NOT FULLY FUNCTIONAL, currently only follows request of searching the first keyword
        """

        print(f"There are {len(self.data)} municipalities")

        # for each municipality
        for item in self.data:
            # item = {"state": "Arizona", "muni": "Douglas", "url": "https://library.municode.com/az/douglas"}

            # tried: "for key in self.keywords", but it seems like it can't send duplicate requests
            print(f"Crawling through {item['state'], item['muni']}")

            # Using playwright to load JS for 6 seconds, types keyword into search bar, presses enter, and then waits
            # 6 seconds for the next page to load. When the page loads, the callback is sent to parse_search.
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
            # !!!! stops once it reaches a site that redirects it to a different site like Preston, ID

    async def parse_search(self, response, state, muni, url):
        """ Scrapes search page for FIRST URL
            (The first URL may not be the one with the parking code) needs further development
            Inserts data into scrapy Item

        """
        print(f"\n\n\nIn parse_search for {muni}, {state}:")

        page = response.meta["playwright_page"]
        await page.close()
        # print(page)
        parking_url = response.xpath('//h4/a/@href').get()

        # add a section to check if the first link is the right ones

        parking_code = ParkingCodeItem()
        parking_code['state'] = state
        parking_code['municipality'] = muni
        parking_code['state_url'] = url
        parking_code['parking_code'] = parking_url
        yield parking_code

    async def errback(self, failure):
        """ Not fully implemented, needs to catch sites that redirects to a different site
        """
        page = failure.request.meta["playwright_page"]
        await page.close()
        print('\n\n\nIn errback\n\n\n')
        # need to deal with site redirects like Alpine, Utah

