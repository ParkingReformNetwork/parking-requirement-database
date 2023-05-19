# spiders/quotes.py

import scrapy
from ..items import StateItem, MuniItem
from scrapy_playwright.page import PageMethod


class MunispiderSpider(scrapy.Spider):
    name = 'munispider'
    allowed_domains = ['library.municode.com']
    start_url = ['https://library.municode.com']
    custom_settings = {
        'FEEDS': {
            'municipalities.json': {'format': 'json'}
        }
    }

    def start_requests(self):
        url = "https://library.municode.com"
        yield scrapy.Request(url, callback=self.parse_state,
                             meta=dict(
                                 playwright=True,
                                 playwright_include_page=True,
                                 playwright_page_methods=[PageMethod('wait_for_selector', 'h3.text-divider')],
                                 errback=self.errback,
                             ))

    async def parse_state(self, response):
        print("\n\n\nIn parse:")
        page = response.meta["playwright_page"]
        await page.close()

        for s in response.xpath('//ul[@class = "nav row"]/child::li/a'):    # navigates to each state
            relative_url = s.xpath('@href').get()   # gets embedded link
            print(f'\n\n\nFollowing {relative_url}:')
            yield scrapy.Request(relative_url, callback=self.parse_muni_page,
                                 meta=dict(playwright=True,
                                           playwright_include_page=True,
                                           playwright_page_methods=[PageMethod('wait_for_selector', 'h3.text-divider')],
                                           errback=self.errback,
                                           ))      # follows embedded link

    async def parse_muni_page(self, response):
        print("\n\n\nIn parse_muni_page:")
        page = response.meta["playwright_page"]
        await page.close()

        state = response.xpath('//section[@id = "primary"]//h2/text()').get()
        for m in response.xpath('//ul[@class = "nav row"]/child::li/a'):  # navigates to each municipality
            muni_item = MuniItem()
            muni_item['state'] = state  # gets state
            muni_item['muni'] = m.xpath('text()').get()  # gets municipality
            muni_item['url'] = m.xpath('@href').get()  # gets embedded link
            yield muni_item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

