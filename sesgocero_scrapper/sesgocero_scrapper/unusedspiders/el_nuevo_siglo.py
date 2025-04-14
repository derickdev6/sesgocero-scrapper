# This is a spider for the website elnuevosiglo.com

import scrapy
from bs4 import BeautifulSoup
from ..items import NewsItem
from datetime import datetime
from urllib.parse import urljoin
import re
import logging

# Set up logging
logging.basicConfig(level=logging.CRITICAL)  # Change to WARNING or higher


class ElNuevoSigloSpider(scrapy.Spider):
    name = "el_nuevo_siglo"
    start_urls = ["https://www.elnuevosiglo.com.co/politica-0"]
    custom_settings = {
        # "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,  # Add delay between requests
        "CONCURRENT_REQUESTS": 16,
    }

    def parse(self, response):
        # Extract all article URLs from the page
        article_urls = response.css("h2 a::attr(href)").getall()

        for url in article_urls:
            # Ensure we have absolute URLs
            absolute_url = urljoin(response.url, url)
            yield response.follow(absolute_url, callback=self.parse_article)

    def parse_article(self, response):
        try:
            # Extract title with fallback
            title = response.css("h1::text").get()
            if not title:
                title = None

            # Extract subtitle with fallback
            subtitle = response.css("div.views-field-field-summary::text").get()
            if not subtitle:
                subtitle = None

            # Extract content with better error handling
            content_elements = response.css("div.paragraph p::text")
            content = " ".join(content_elements.getall())
            if not content:
                content = "No content found"

            # Extract date with multiple selectors and better error handling
            date_str = None

            # Try different selectors for the date
            selectors = [
                "span.field--name-created::text",  # Primary selector
            ]

            for selector in selectors:
                date_str = response.css(selector).get()
                if date_str:
                    break

            # Parse the date using our helper method
            date = self.parse_date(date_str)

            # Yield item
            if title and subtitle and content and date:
                yield NewsItem(
                    title=title.strip(),
                    subtitle=subtitle.strip(),
                    content=content,
                    date=date if date else None,
                    url=response.url,
                    source="El Nuevo Siglo",
                    cleaned=False,
                )
        except Exception as e:
            self.logger.error(f"Error parsing article: {e}")

    def parse_date(self, date_str):
        """Helper method to parse different date formats"""
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
            date_str = date_str.split(" , ")[1].strip()

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
