# -*- coding: utf-8 -*-
from datetime import datetime

from datetime import datetime
from urllib import parse

import scrapy
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import ShixiJobItemLoader, ShixiJobItem
from utils.common import get_md5


class ShixisengSpider(CrawlSpider):
    name = 'shixiseng'
    allowed_domains = ['www.shixiseng.com']
    start_urls = ['https://www.shixiseng.com/interns?k=Python&p=1']

    rules = (
        Rule(LinkExtractor(allow=r'intern/.*'), callback='parse_job', follow=False),
        # Rule(LinkExtractor(allow=(r'interns.*'), restrict_css=('.pagination ul li:nth-child(9) a')),
         #    callback='print_url', follow=True),
    )

    def print_url(self, response):
        print('print_url', response.url)

    def parse_start_url(self, response):
        print('parse_start_url', response.url)
        return []

    def parse_job(self, response):
        item_loader = ShixiJobItemLoader(item=ShixiJobItem(), response=response)
        item_loader.add_css("job_name", ".new_job_name::attr(title)")
        item_loader.add_value("job_url", response.url)
        item_loader.add_value("url_obj_id", get_md5(response.url))
        item_loader.add_css("job_date", ".job_date .cutom_font::text")
        item_loader.add_css("job_money", ".job_money.cutom_font::text")
        item_loader.add_css("job_position", ".job_position::text")
        item_loader.add_css("job_academic", ".job_academic::text")
        item_loader.add_css("job_week", ".job_week.cutom_font::text")
        item_loader.add_css("job_time",".job_time.cutom_font::text")
        item_loader.add_css("job_good", ".job_good::text")
        item_loader.add_css("job_detail", ".job_part .job_detail")
        item_loader.add_css("job_com_name", ".job_com_name::text")
        item_loader.add_css("job_com_msg", ".job_detail.job_detail_msg span::text")
        item_loader.add_css("job_link", ".job_link::attr(href)")
        item_loader.add_css("job_till", ".job_detail.cutom_font::text")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()
        # print(job_item)

        return job_item
