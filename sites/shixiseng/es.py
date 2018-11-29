from elasticsearch_dsl import connections, Document, Text, Keyword, Date, Completion, analyzer

connections.create_connection(hosts=["localhost"])

# 最粗粒度的拆分
my_analyzer = analyzer('ik_smart')


class ShixisengIndex(Document):
    suggest = Completion(analyzer=my_analyzer)
    job_name = Text(analyzer="ik_max_word")
    job_url = Keyword()
    url_obj_id = Keyword()
    job_money = Keyword()
    job_time = Date()
    job_date = Date()
    job_till = Date()
    job_week = Keyword()
    job_academic = Keyword()
    job_position = Keyword()
    job_good = Text(analyzer="ik_smart")
    job_detail = Text(analyzer="ik_smart")
    job_com_name = Keyword()
    job_com_msg = Keyword()
    job_link = Keyword()
    #crawl_time = Date()

    class Index:
        name = 'shixiseng_job',


if __name__ == "__main__":
    ShixisengIndex.init()

