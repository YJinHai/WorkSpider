from elasticsearch_dsl import connections, Document, Text, Keyword, Date, Completion, analyzer

connections.create_connection(hosts=["localhost"])

# 最粗粒度的拆分
my_analyzer = analyzer('ik_smart')


class LagouIndex(Document):
    suggest = Completion(analyzer=my_analyzer)
    position_name = Text(analyzer="ik_max_word")
    url = Keyword()
    url_obj_id = Keyword()
    salary = Keyword()
    city = Keyword()
    create_time = Date()
    work_years = Keyword()
    job_nature = Keyword()
    education = Keyword()
    district = Keyword()
    description = Text(analyzer="ik_smart")
    linestaion = Keyword()
    company_full_name = Keyword()
    company_size = Keyword()
    lables = Text(analyzer="ik_max_word")
    crawl_time = Date()

    class Index:
        name = 'lagou_job',



if __name__ == "__main__":
    LagouIndex.init()