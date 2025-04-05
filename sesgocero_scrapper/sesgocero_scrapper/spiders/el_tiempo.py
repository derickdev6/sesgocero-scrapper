# This is a spider for the website eltiempo.com

import scrapy
from bs4 import BeautifulSoup
from ..items import NewsItem
from datetime import datetime
from urllib.parse import urljoin
import re


class ElTiempoSpider(scrapy.Spider):
    name = "el_tiempo"
    start_urls = ["https://www.eltiempo.com/politica/gobierno/"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,  # Add delay between requests
        "CONCURRENT_REQUESTS": 16,
    }

    def parse(self, response):
        # Extract all article URLs from the page
        article_urls = response.css("h3.c-articulo__titulo a::attr(href)").getall()

        for url in article_urls:
            # Ensure we have absolute URLs
            absolute_url = urljoin(response.url, url)
            yield response.follow(absolute_url, callback=self.parse_article)

    def parse_article(self, response):
        try:
            # Extract title with fallback
            title = response.css("h1.c-articulo__titulo::text").get()
            if not title:
                title = response.css("h1::text").get()

            # Extract subtitle with fallback
            subtitle = response.css("h2.c-lead__titulo::text").getall()
            subtitle = " ".join(subtitle) if subtitle else None
            if not subtitle:
                subtitle = response.css("h2::text").get()

            # Extract content with better error handling
            content_elements = response.css("div.paragraph")
            content = []
            for element in content_elements:
                html_content = element.getall()
                html_content = "".join(html_content)
                if html_content:
                    text = BeautifulSoup(html_content, "html.parser").get_text(
                        strip=True
                    )
                    if text:
                        content.append(text)

            # Extract date with multiple selectors and better error handling
            date_str = None

            # Try different selectors for the date
            selectors = [
                "div.c-articulo__autor__fecha time::text",  # Primary selector
                "div.c-articulo__autor__fecha span time::text",  # Fallback 1
                "div.c-articulo__autor__fecha span::text",  # Fallback 2
                "time::attr(datetime)",  # Fallback 3
                "div.c-articulo__autor__fecha time::attr(datetime)",  # Fallback 4
            ]

            for selector in selectors:
                date_str = response.css(selector).get()
                if date_str:
                    break

            # Parse the date using our helper method
            date = self.parse_date(date_str)

            # Only yield if we have at least a title and some content
            if title and content:
                yield NewsItem(
                    id="ElTiempo_" + title.strip(),
                    title=title.strip(),
                    subtitle=subtitle.strip() if subtitle else None,
                    content=content,
                    date=date,
                    url=response.url,
                    source="El Tiempo",
                    processed=False,
                )
            else:
                self.logger.warning(
                    f"Missing required fields for article: {response.url}"
                )
        except Exception as e:
            self.logger.error(f"Error parsing article {response.url}: {str(e)}")

    def parse_date(self, date_str):
        """Helper method to parse different date formats"""
        if not date_str:
            return None

        try:
            # Try to parse ISO format first
            if "T" in date_str:
                date_str = date_str.split("T")[0]
                return datetime.strptime(date_str, "%Y-%m-%d")

            # Try to parse Spanish date format
            pattern = r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})"
            match = re.search(pattern, date_str.lower())

            if match:
                day, month, year = match.groups()
                # Spanish month mapping
                month_map = {
                    "enero": "01",
                    "febrero": "02",
                    "marzo": "03",
                    "abril": "04",
                    "mayo": "05",
                    "junio": "06",
                    "julio": "07",
                    "agosto": "08",
                    "septiembre": "09",
                    "octubre": "10",
                    "noviembre": "11",
                    "diciembre": "12",
                }
                month_num = month_map.get(month.lower())
                if month_num:
                    formatted_date = f"{year}-{month_num}-{day.zfill(2)}"
                    return datetime.strptime(formatted_date, "%Y-%m-%d")

            # Try standard formats as last resort
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    self.logger.warning(f"Could not parse date: {date_str}")
                    return None

        except Exception as e:
            self.logger.warning(f"Error parsing date {date_str}: {str(e)}")
            return None
