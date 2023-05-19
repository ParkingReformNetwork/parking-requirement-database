# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    pass


class MuniItem(scrapy.Item):
    state = scrapy.Field()
    muni = scrapy.Field()
    url = scrapy.Field()

