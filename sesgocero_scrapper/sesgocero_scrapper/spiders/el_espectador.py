# This is a spider for the website elespectador.com

import scrapy
from bs4 import BeautifulSoup
from ..items import NewsItem
from datetime import datetime
from urllib.parse import urljoin
import re


class ElEspectadorSpider(scrapy.Spider):
    name = "el_espectador"
    start_urls = ["https://www.elespectador.com/"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,  # Add delay between requests
        "CONCURRENT_REQUESTS": 16,
    }

    def parse(self, response):
        # Extract all article URLs from the page
        article_urls = response.css("h2.Card-Title a::attr(href)").getall()

        for url in article_urls:
            # Ensure we have absolute URLs
            absolute_url = urljoin(response.url, url)
            yield response.follow(absolute_url, callback=self.parse_article)

    def parse_article(self, response):
        try:
            # Extract title with fallback
            title = response.css("h1.Title::text").get()
            if not title:
                title = response.css("h1::text").get()

            # Extract subtitle with fallback
            subtitle = response.css("h2.ArticleHeader-Hook div::text").get()
            if not subtitle:
                subtitle = response.css("h2::text").get()

            # Extract content with better error handling
            content_elements = response.css("p.font--secondary::text")
            content = []
            for element in content_elements:
                html_content = element.get()
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
                "div.Datetime::text",  # Try text content first
                "div.Card-Date span::text",
                "div.Card-Date a::text",
                "div.Article-Date::text",
                "div.Article-Header time::text",
            ]

            for selector in selectors:
                date_str = response.css(selector).get()
                if date_str:
                    break

            # Parse the date using our helper method
            date = self.parse_date(date_str)

            # Only yield if we have at least a title and some content
            if title and content:
                item = NewsItem(
                    title=title.strip(),
                    subtitle=subtitle.strip() if subtitle else None,
                    content=content,
                    date=date,
                    url=response.url,
                    source="El Espectador",
                )
                yield item
        except Exception as e:
            self.logger.error(f"Error parsing article: {e}")
            pass

    def parse_date(self, date_str):
        """Helper method to parse Spanish date formats"""
        if not date_str:
            return None

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

        try:
            # Remove time information if present
            date_str = date_str.split(" - ")[0].strip()

            # Extract day, month, and year using regex
            pattern = r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})"
            match = re.search(pattern, date_str.lower())

            if match:
                day, month, year = match.groups()
                # Convert Spanish month name to number
                month_num = month_map.get(month.lower())
                if month_num:
                    # Format as YYYY-MM-DD
                    formatted_date = f"{year}-{month_num}-{day.zfill(2)}"
                    return datetime.strptime(formatted_date, "%Y-%m-%d")

            self.logger.warning(f"Could not parse Spanish date format: {date_str}")
            return None

        except Exception as e:
            self.logger.warning(f"Error parsing date {date_str}: {str(e)}")
            return None
