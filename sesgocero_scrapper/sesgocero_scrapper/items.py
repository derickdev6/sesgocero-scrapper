# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    id = scrapy.Field(unique=True)
    title = scrapy.Field()
    subtitle = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    cleaned = scrapy.Field()
    political_orientation = scrapy.Field()
