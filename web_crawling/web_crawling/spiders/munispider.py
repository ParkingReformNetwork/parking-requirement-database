# spiders/quotes.py

import scrapy
from ..items import MuniItem
from scrapy_playwright.page import PageMethod


class MunispiderSpider(scrapy.Spider):
    name = 'munispider'
    allowed_domains = ['library.municode.com']
    start_url = ['https://library.municode.com']


    def start_requests(self):
        url = "https://library.municode.com"
        yield scrapy.Request(url, meta=dict(
            playwright=True,
            playwright_include_page=True,
            playwright_page_methods=[PageMethod('wait_for_selector', 'h3.text-divider')],
            errback=self.errback,
        ))

    async def parse(self, response):
        print("\n\n\nIn parse:")
        page = response.meta["playwright_page"]
        await page.close()

        for muni in response.xpath('//ul[@class = "nav row"]/child::li/a/text()'):
            muni_item = MuniItem()
            muni_item['name'] = muni.get()
            yield muni_item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

