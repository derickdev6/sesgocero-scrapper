import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    subtitle = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field(unique=True)
    source = scrapy.Field()
    cleaned = scrapy.Field()
