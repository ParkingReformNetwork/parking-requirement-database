# spiders/quotes.py

import scrapy
import os
from ..items import StateItem
from scrapy_playwright.page import PageMethod


class StatespiderSpider(scrapy.Spider):
    name = 'statespider'
    allowed_domains = ['library.municode.com']
    start_url = ['https://library.municode.com']

    state_dir = os.path.join('jsons', 'states.json')
    custom_settings = {
        'FEEDS': {
            state_dir: {
                'format': 'json',
                'overwrite': True}
        }
    }

    def start_requests(self):
        url = "https://library.municode.com"
        yield scrapy.Request(url, callback=self.parse_state, meta=dict(
            playwright=True,
            playwright_include_page=True,
            playwright_page_methods=[PageMethod('wait_for_selector', 'h3.text-divider')],
            errback=self.errback,
        ))

    async def parse_state(self, response):
        print("\n\n\nIn parse:")
        page = response.meta["playwright_page"]
        await page.close()

        for s in response.xpath('//ul[@class = "nav row"]/child::li/a'):
            state_item = StateItem()
            state_item['name'] = s.xpath('text()').get()

            state_item['url'] = s.xpath('@href').get()
            yield state_item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

