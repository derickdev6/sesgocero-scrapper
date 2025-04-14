# run_all_spiders.py
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy import spiderloader


def run_all():
    settings = get_project_settings()
    configure_logging(settings)
    process = CrawlerProcess(settings)

    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    for spider_name in spider_loader.list():
        print(f"\n\nEjecutando spider: {spider_name}\n{30*'-*-'}\n")
        process.crawl(spider_name)

    process.start()


if __name__ == "__main__":
    run_all()
