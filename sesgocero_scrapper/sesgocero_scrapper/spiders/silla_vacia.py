# This is a spider for the website lasillavacia.com

import scrapy
from ..items import NewsItem
from datetime import datetime
from urllib.parse import urljoin
import logging

# Set up logging
logging.basicConfig(level=logging.CRITICAL)  # Change to WARNING or higher


class SillaVaciaSpider(scrapy.Spider):
    name = "silla_vacia"
    start_urls = ["https://www.lasillavacia.com/"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,  # Add delay between requests
        "CONCURRENT_REQUESTS": 16,
    }

    def parse(self, response):
        # Extract all article URLs from the page
        article_urls = response.css("h2.entry-title a::attr(href)").getall()

        for url in article_urls:
            # Ensure we have absolute URLs
            absolute_url = urljoin(response.url, url)
            yield response.follow(absolute_url, callback=self.parse_article)

    def parse_article(self, response):
        try:
            # Extract title with fallback
            title = response.css("h1.entry-title::text").get()
            if not title:
                title = None

            # Extract subtitle with fallback
            subtitle = response.css("h2.entry-title::text").get()
            if not subtitle:
                subtitle = None

            # Extract content with better error handling
            content_elements = response.css("div.entry-content p::text")
            content = " ".join(content_elements.getall())
            if not content:
                content = "No content found"

            # Extract date with multiple selectors and better error handling
            date_str = None

            # Try different selectors for the date
            selectors = [
                "span.posted-on time.published::attr(datetime)",  # Primary selector
            ]

            for selector in selectors:
                date_str = response.css(selector).get()
                if date_str:
                    break

            # Parse the date using our helper method
            date = self.parse_date(date_str)

            # Yield item
            if title and content and date:
                yield NewsItem(
                    title=title.strip(),
                    subtitle=subtitle.strip() if subtitle else "",
                    content=content,
                    date=date if date else None,
                    url=response.url,
                    source="La Silla Vacia",
                    cleaned=False,
                )
            else:
                self.logger.warning(
                    f"Skipping article {response.url}: Missing required fields\n{10*'*-'}\n{title}\n{subtitle}\n{content[:50]}\n{date}\n{10*'*-'}\n"
                )
        except Exception as e:
            self.logger.error(f"Error parsing article {response.url}: {str(e)}")

    def parse_date(self, date_str):
        """Helper method to parse different date formats"""
        if not date_str:
            return None

        # Remove any timezone information if present
        date_str = date_str.split("T")[0]

        try:
            # Try the standard format first
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                # Try alternative format if present
                return datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                self.logger.warning(f"Could not parse date: {date_str}")
                return None
