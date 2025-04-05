from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sesgocero_scrapper.spiders.el_tiempo import ElTiempoSpider
from sesgocero_scrapper.spiders.el_pais import ElPaisSpider
from sesgocero_scrapper.spiders.el_espectador import ElEspectadorSpider


def run_spiders():
    process = CrawlerProcess(get_project_settings())
    process.crawl(ElTiempoSpider)
    process.crawl(ElPaisSpider)
    process.crawl(ElEspectadorSpider)
    process.start()


if __name__ == "__main__":
    run_spiders()
