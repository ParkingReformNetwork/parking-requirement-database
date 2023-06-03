# spiders/quotes.py

import scrapy
import os
from ..items import MuniItem
from scrapy_playwright.page import PageMethod


class MunispiderSpider(scrapy.Spider):
    """
    Crawls through home page of municode for URL links for every municipality
    Includes following links into every state, and then every municipality
    """
    name = 'munispider'
    allowed_domains = ['library.municode.com']
    start_url = ['https://library.municode.com']

    muni_dir = os.path.join('jsons', 'municipalities.json')
    custom_settings = {
        'FEEDS': {
            muni_dir: {
                'format': 'json',
                'overwrite': True}
        }
    }

    def start_requests(self):
        """
        Requests for Municode's home page. Response is sent to parse_state.
        """
        url = "https://library.municode.com"

        # waits for page to load a specific header
        # this can be changed into wait for a certain amount of time
        yield scrapy.Request(url, callback=self.parse_state,
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 playwright_page_methods=[PageMethod('wait_for_selector', 'h3.text-divider')],
                                 errback=self.errback,
                             ))

    async def parse_state(self, response):
        """
        Follows link into each state. Response is sent to parse_muni_page.
        """
        page = response.meta["playwright_page"]
        await page.close()

        for s in response.xpath('//ul[@class = "nav row"]/child::li/a'):    # navigates to each state
            relative_url = s.xpath('@href').get()   # gets embedded link
            print(f'\n\n\nFollowing {relative_url}:')
            yield scrapy.Request(relative_url, callback=self.parse_muni_page,
                                 meta=dict(playwright=True,
                                           playwright_include_page=True,
                                           playwright_page_methods=
                                           [PageMethod('wait_for_selector', 'div.navbar-search')],  # wait for nav bar
                                           errback=self.errback,
                                           ))      # follows embedded link

    async def parse_muni_page(self, response):
        """
        Scrapes each municipality URL in the state site. Inserts into a scrapy item.
        Should be called x times for x states.
        """
        print("\n\n\nIn parse_muni_page:")
        page = response.meta["playwright_page"]
        await page.close()

        state = response.xpath('//section[@id = "primary"]//h2/text()').get()
        for m in response.xpath('//ul[@class = "nav row"]/child::li/a'):  # navigates to each municipality
            muni_item = MuniItem()
            muni_item['state'] = state  # gets state
            muni_item['municipality'] = m.xpath('text()').get()  # gets municipality
            muni_item['url'] = m.xpath('@href').get()  # gets embedded link
            yield muni_item

    async def errback(self, failure):
        """
        To be implemented fully
        """
        page = failure.request.meta["playwright_page"]
        await page.close()

