# This is a spider for the website elpais.com

import scrapy
from bs4 import BeautifulSoup
from ..items import NewsItem
from datetime import datetime
from urllib.parse import urljoin
import logging

# Set up logging
logging.basicConfig(level=logging.CRITICAL)  # Change to WARNING or higher


class ElPaisSpider(scrapy.Spider):
    name = "el_pais"
    start_urls = ["https://elpais.com/america-colombia/actualidad/"]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,  # Add delay between requests
        "CONCURRENT_REQUESTS": 16,
    }

    def parse(self, response):
        # Extract all article URLs from the page
        article_urls = response.css("h2.c_t a::attr(href)").getall()

        for url in article_urls:
            # Ensure we have absolute URLs
            absolute_url = urljoin(response.url, url)
            yield response.follow(absolute_url, callback=self.parse_article)

    def parse_article(self, response):
        try:
            # Extract title with fallback
            title = response.css("h1.a_t::text").get()
            if not title:
                title = None

            # Extract subtitle with fallback
            subtitle = response.css("h2.a_st::text").get()
            if not subtitle:
                subtitle = None

            # Extract content with better error handling
            content_elements = response.css("div.a_c p, div.a_c h2")
            # Join all content elements into a single string
            content = " ".join(content_elements.getall())
            if not content:
                content = "No content found"

            # Extract date with multiple selectors and better error handling
            date_str = None

            # Try different selectors for the date
            selectors = [
                "div.a_md_f a::attr(data-date)",  # Primary selector
            ]

            for selector in selectors:
                date_str = response.css(selector).get()
                print(f"Date string: {date_str}\n{30*'*-'}")
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
                    source="El Pais",
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
