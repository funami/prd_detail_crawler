# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['http://www.biccamera.com/bc/c/contents/sitemap/index.jsp']
    start_urls = ['http://http://www.biccamera.com/bc/c/contents/sitemap/index.jsp/']

    def parse(self, response):
        pass
