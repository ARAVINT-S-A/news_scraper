# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import itertools

from scrapy import Spider, crawler, signals
from scrapy.exceptions import IgnoreRequest

from .utils import get_interface_ips, get_output_urls


class NewsScraperDownloaderMiddleware:
    floating_ips = get_interface_ips()
    output_urls = []

    @property
    def floating_ips_cycle(self):
        return itertools.cycle(self.floating_ips)

    @classmethod
    def from_crawler(cls, crawler: crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider: Spider):
        # ignore urls which are already processed
        if request.url in self.output_urls:
            spider.logger.info("Ignoring Request (already in output): %s", request.url)
            raise IgnoreRequest

        # sample web proxy usage
        # request.meta["proxy"] = "http://user:pass@brd.superproxy.io:22225"

        # use all ips available on server
        if spider.settings.get("USE_FLOATING_IPS"):
            if self.floating_ips:
                request.meta["bindaddress"] = (next(self.floating_ips_cycle), 0)

        return None

    def spider_opened(self, spider: Spider):
        spider.logger.info("Spider opened: %s" % spider.name)

        spider.logger.info(
            "Floating IPs (total: %s): %s" % (len(self.floating_ips), self.floating_ips)
        )

        # load already parsed urls
        if spider.settings.get("SKIP_OUTPUT_URLS"):
            # TODO: the file path should be loaded dynamically from the spider's FEEDS settings
            output_file = f"outputs/{spider.name}.jl"
            self.output_urls = get_output_urls(output_file)
            spider.logger.info(
                "Already scraped %s URLs in: %s" % (len(self.output_urls), output_file)
            )
