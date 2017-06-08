# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

class BiccameraSpider(scrapy.Spider):
    name = "biccamera"
    start_urls = [
        'http://www.biccamera.com/bc/c/contents/sitemap/index.jsp'
    ]

    @staticmethod
    def _extract_disp_no(url):
        dispNo = re.findall(r'dispNo=(\d+)', url) 
        if len(dispNo) == 1:
            return dispNo[0]
        else:
            return None
        
    def parse(self, response):
        for link in response.css('div.tolinkcategory'):
            url = link.css('a::attr("href")').extract_first()
            dispNo = self._extract_disp_no(url) 
            if dispNo is not None:
                yield {
                    'type': 'category_top',
                    'parent': None,
                    'no': dispNo,
                    'name': link.css('a::text').extract_first(),
                    'url': url,
                }
                yield response.follow(url, self.page_parse)

    def page_parse(self, response):
        parent_dispNo = self._extract_disp_no(response.url) 
        count_cat_link = 0
        for link in response.css('#catNav ul >li >a'):
            url = link.css('::attr("href")').extract_first()
            dispNo = self._extract_disp_no(url) 
            if dispNo is not None and re.match(dispNo, parent_dispNo) is None:
                yield {
                    'type': 'category',
                    'parent': parent_dispNo,
                    'no': dispNo,
                    'name': link.css('a::text').extract_first(),
                    'url': url,
                }
                yield response.follow(url, self.page_parse)
                count_cat_link += 1

        # これ以上、細分化したカテゴリーがない場合
        if count_cat_link == 0:
            next_page = response.css('.footNav p.next a::attr("href")').extract_first()
            for prod_box in response.css('.prod_box'):
                detail = prod_box.css('.detail')
                link = detail.css('.name a::attr("href")').extract_first()
                goods_no = re.findall(r'GOODS_NO=(\d+)', link) 
                if len(goods_no) == 1:
                    yield {
                        'type': 'detail',
                        'disp_no': dispNo,
                        'name': detail.css('.name a::text').extract_first(),
                        'goods_no': goods_no[0],
                        'stock': prod_box.css('.label_cell.active>span::text').extract_first(),
                        'bic_price': detail.css('span.val::text').extract_first().replace(r',',''),
                        'time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    }
            if next_page is not None:
                 yield response.follow(next_page, self.page_parse)

