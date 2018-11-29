# -*- coding: utf-8 -*-
import json
import random
import time
from datetime import datetime

import scrapy
from scrapy import FormRequest
from scrapy.spiders import CrawlSpider, Rule


from utils.common import get_md5
from items import LagouJobItemLoader, LagouItem


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/jobs/positionAjax.json?']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; set=UTF-8',
        'Cookie': 'JSESSIONID=ABAAABAAAGFABEF2A9F526EEAF8A4D5979C9C91C470D916; user_trace_token=20181108222228-77038827-4d01-4f91-8b3a-55a0cccaf9d6; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1541686949; _ga=GA1.2.1567223367.1541686949; _gid=GA1.2.489493353.1541686949; LGUID=20181108222230-b9c05f9e-e361-11e8-9314-525400f775ce; TG-TRACK-CODE=search_code; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1541777035; LGRID=20181109232414-8446b9ff-e433-11e8-94aa-525400f775ce; SEARCH_ID=e89119713fd54563ad1b598a8c7e631a',
        'Referer': 'https://www.lagou.com/jobs/list_Python?labelWords=&fromSearch=true&suginput=1',
        'Host': 'www.lagou.com',
        'Origin': 'https: // www.lagou.com',
        'X-Anit-Forge-Code': 0,
        'X-Anit-Forge-Token': None,
        'X-Requested-With': 'XMLHttpRequest'
    }

    page = 1

    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url, headers=self.headers,
                              formdata={
                                  'first': 'true',
                                  'pn': str(self.page),
                                  'kd': 'Python',
                                  'city': '深圳'

                              }, callback=self.parse,
                              dont_filter=True
                              )

    def parse_start_url(self, response):

        data = json.loads(response.body.decode('utf-8'))
        result = data['content']['positionResult']['result']
        totalCount = data['content']['positionResult']['totalCount']
        resultSize = data['content']['positionResult']['resultSize']

        for each in result:
            item = LagouItem()
            item['url'] = 'https://www.lagou.com/jobs/{}.html'.format(each['positionId'])
            res = scrapy.Request(url=item['url'], headers=self.headers, callback=self.detail_parse)
            res.meta['item'] = item
            res.meta['each'] = each
            yield res

            time.sleep(0.1)

        time.sleep(random.randint(1, 5))

        if int(resultSize):
            self.allpage = int(totalCount) / int(resultSize) + 1
            if self.page < self.allpage:
                self.page += 1
                yield FormRequest(self.start_urls[0], headers=self.headers,
                                  formdata={
                                      'first': 'false',
                                      'pn': str(self.page),
                                      'kd': 'Python',
                                      'city': '深圳'
                                  }, callback=self.parse
                                  )

    def detail_parse(self, response):

        item = response.meta['item']
        des = response.css('.job_bt div p').extract()
        item['description'] = ",".join(des)

        each = response.meta['each']
        item['url_obj_id'] = get_md5(item['url'])
        item['lables'] = ",".join(each['positionLables'])
        item['city'] = each['city']
        item['company_full_name'] = each['companyFullName']
        item['company_size'] = each['companySize']
        item['district'] = each['district']
        item['education'] = each['education']
        item['linestaion'] = each['linestaion']
        item['position_name'] = each['positionName']
        item['job_nature'] = each['jobNature']
        item['salary'] = each['salary']
        item['create_time'] = each['createTime']
        item['work_year'] = each['workYear']
        item["crawl_time"] = datetime.now()

        yield item
