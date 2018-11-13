# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re

import scrapy
from scrapy.loader import ItemLoader, wrap_loader_context
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.utils.datatypes import MergeDict
from scrapy.utils.misc import arg_to_iter


from utils.Shixiseng_encode import ShiXi
from utils.common import extract_num



class WorkspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TakeFirstCustom(TakeFirst):
    def __call__(self, values):
        for value in values:
            if value is not None and value != '':
                return value.strip() if isinstance(value, str) else value


class MapComposeCustom(MapCompose):
    #自定义MapCompose，当value没元素时传入" "
    def __call__(self, value, loader_context=None):
        if not value:
            value.append(" ")
        values = arg_to_iter(value)
        if loader_context:
            context = MergeDict(loader_context, self.default_loader_context)
        else:
            context = self.default_loader_context
        wrapped_funcs = [wrap_loader_context(f, context) for f in self.functions]
        for func in wrapped_funcs:
            next_values = []
            for v in values:
                next_values += arg_to_iter(func(v))
            values = next_values
        return values


class ShixiJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_input_processor = MapComposeCustom()
    default_output_processor = TakeFirstCustom()


def date_convert(value):
    value = value.split(' ')[0]
    try:
        create_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


shixi_encode = ShiXi()
shixi_encode.start_crawl()


def num_convert(value):
    # 处理scrapy爬取下来的字符直接乱码打印，转为'\u'开头的
    value = value.encode('unicode_escape').decode()
    return shixi_encode.modify_data(value)


class ShixiJobItem(scrapy.Item):
    # 实习僧职位信息
    job_name = scrapy.Field()
    job_url = scrapy.Field()
    url_obj_id = scrapy.Field()
    job_date = scrapy.Field(
        input_processor=MapCompose(num_convert, date_convert),
    )
    job_money = scrapy.Field(
        input_processor=MapCompose(num_convert, extract_num),
    )
    job_position = scrapy.Field()
    job_academic = scrapy.Field()
    job_week = scrapy.Field(
        input_processor=MapCompose(num_convert, extract_num),
    )
    job_time = scrapy.Field(
        input_processor=MapCompose(num_convert, extract_num),
    )
    job_good = scrapy.Field()
    job_detail = scrapy.Field()
    job_com_name = scrapy.Field()
    job_com_msg = scrapy.Field(
        input_processor=Join(",")
    )
    job_link = scrapy.Field()
    job_till = scrapy.Field(
        input_processor=MapCompose(num_convert, date_convert),
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert ignore  into  shixiseng_job(url_obj_id, job_name, job_url, job_date, job_money, 
                    job_position, job_academic, job_week, job_time, job_good, 
                    job_detail,job_com_name, job_com_msg, job_link, job_till, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params =(
            self["url_obj_id"], self["job_name"], self["job_url"], self["job_date"],
            self["job_money"], self["job_position"], self["job_academic"], self["job_week"],
            self["job_time"], self["job_good"], self["job_detail"], self["job_com_name"],
            self["job_com_msg"], self["job_link"], self["job_till"], self["crawl_time"]
        )

        return insert_sql, params
