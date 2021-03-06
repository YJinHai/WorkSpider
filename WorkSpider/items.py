# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy
from elasticsearch_dsl import connections
from scrapy.loader import ItemLoader, wrap_loader_context
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.utils.datatypes import MergeDict
from scrapy.utils.misc import arg_to_iter

from utils.es_tuils import generate_suggests
from sites.lagou.es import LagouIndex
from sites.shixiseng.es import ShixisengIndex

from utils.Shixiseng_encode import ShiXi
from utils.common import extract_num

es_lagou_job = connections.create_connection(LagouIndex)
es_shixiseng_job = connections.create_connection(ShixisengIndex)
JOB_COUNT_INIT = 0

SQL_DATETIME_FORMAT = "%Y-%m-%d"


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
    # 自定义MapCompose，当value没元素时传入" "
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

        params = (
            self["url_obj_id"], self["job_name"], self["job_url"], self["job_date"],
            self["job_money"], self["job_position"], self["job_academic"], self["job_week"],
            self["job_time"], self["job_good"], self["job_detail"], self["job_com_name"],
            self["job_com_msg"], self["job_link"], self["job_till"], self["crawl_time"]
        )

        return insert_sql, params

    def save_to_es(self):
        job = ShixisengIndex(meta={'id': self['url_obj_id']})
        job.url_obj_id = self["url_obj_id"]
        job.job_url = self["job_url"]
        job.job_name = self["job_name"]
        job.job_date = self["job_date"]
        job.job_money = self["job_money"]
        job.job_position = self["job_position"]
        job.job_academic = self["job_academic"]
        job.job_week = self["job_week"]
        job.job_time = self["job_time"]
        job.job_good = self["job_good"]
        job.job_detail = self["job_detail"]
        job.job_com_name = self["job_com_name"]
        job.job_com_msg = self["job_com_msg"]
        job.job_link = self["job_link"]
        job.job_till = self["job_till"]
        # job.crawl_time = self["crawl_time"]

        job.suggest = generate_suggests(es_shixiseng_job, "shixiseng_job",
                                        ((job.job_name, 10), (job.job_good, 7),
                                         (job.job_com_name, 8), (job.job_academic, 3)))

        # real_time_count('lagou_job_count', JOB_COUNT_INIT)

        job.save()


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


# 拉钩职位信息
class LagouItem(scrapy.Item):
    # url
    url = scrapy.Field()

    # 数据库主键
    url_obj_id = scrapy.Field()

    description = scrapy.Field()

    lables = scrapy.Field()

    # 城市
    city = scrapy.Field()

    # 公司
    company_full_name = scrapy.Field()

    # 公司规模
    company_size = scrapy.Field()

    # 地区
    district = scrapy.Field()

    # 教育程度
    education = scrapy.Field()

    # 地点
    linestaion = scrapy.Field()

    # 招聘职务
    position_name = scrapy.Field()

    # 招聘要求
    job_nature = scrapy.Field()

    # 工资
    salary = scrapy.Field()

    # 工作经验
    work_year = scrapy.Field()

    # 岗位发布时间
    create_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )

    crawl_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )

    def get_insert_sql(self):
        insert_sql = """
                    insert IGNORE into lagou_job(url_obj_id, url, position_name, lables, salary, description, city, work_year, company_full_name,
                    company_size, district, education, linestaion, job_nature, create_time,
                    crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

        sql_params = (
            self["url_obj_id"],
            self["url"],
            self["position_name"],
            self['lables'],
            self["salary"],
            self["description"],
            self["city"],
            self["work_year"],
            self["company_full_name"],
            self["company_size"],
            self["district"],
            self["education"],
            self["linestaion"],
            self["job_nature"],
            self["create_time"],
            self["crawl_time"]
        )

        return insert_sql, sql_params

    def save_to_es(self):
        job = LagouIndex(meta={'id': self['url_obj_id']})
        job.url_obj_id = self["url_obj_id"]
        job.url = self["url"]
        job.position_name = self["position_name"]
        job.lables = self['lables']
        job.salary = self["salary"]
        job.description = self["description"]
        job.city = self["city"]
        job.work_years = self["work_year"]
        job.company_full_name = self["company_full_name"]
        job.company_size = self["company_size"]
        job.district = self["district"]
        job.education = self["education"]
        job.linestaion = self["linestaion"]
        job.job_nature = self["job_nature"]
        job.create_time = self["create_time"]
        job.crawl_time = self["crawl_time"]

        job.suggest = generate_suggests(es_lagou_job, "lagou_job",
                                        ((job.position_name, 10), (job.lables, 7), (job.job_nature, 6),
                                         (job.linestaion, 3), (job.company_full_name, 8), (job.description, 5),
                                         (job.city, 9)))
        # real_time_count('lagou_job_count', JOB_COUNT_INIT)

        job.save()
