import json
import asyncio
from datetime import datetime
from time import sleep

import aiohttp
import pandas as pd
import requests
from openpyxl import Workbook


class GkJob:
    def __init__(self):
        self.companyname = []
        self.job_name = []
        self.wage_min = []
        self.wage_max = []
        self.education = []
        self.major = []
        self.amount = []
        self.content = []
        self.page = 1

    def start(self, url):
        self.get_list(url)
        # http://gdit.jobsys.cn/unijob/index.php/wx/jobfair/com_lists?id=70&page_size=10&p=1

    async def get_info(self, url_id):
        url = 'http://gdit.jobsys.cn/unijob/index.php/wx/jobfair/com_jobs?jobfair_id=70&com_id=' + url_id
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession(loop=loop) as session:
            async with session.get(url) as r:
                data = await r.text()
                data = json.loads(data)

                for item in data['jobs']:
                    self.job_name.append(item['job_name'])
                    self.wage_min.append(item['wage_min'])
                    self.wage_max.append(item['wage_max'])
                    self.education.append(item['education_cn'])
                    self.major.append(item['major_cn'])
                    self.amount.append(item['amount'])
                    self.content.append(item['content'])
                    self.companyname.append(data['companyname'])

                result = {
                    '公司名称': self.companyname, '岗位': self.job_name, '最低薪酬': self.wage_min,
                    '最高薪酬': self.wage_max, '学历要求': self.education, '专业要求': self.major,
                    '招聘人数': self.amount, '职位要求': self.content
                }

                df = pd.DataFrame.from_dict(result)
                df.to_excel('GkJob1.xls')

                return result

    def get_list(self, url):
        response = requests.get(url + str(self.page))
        data = json.loads(response.text)
        list_row = data['listRows']
        total_pages = data['total_pages']
        tasks = []
        for item in data['items']:
            tasks.append(asyncio.ensure_future(self.get_info(item['id'])))
        task = asyncio.gather(*tasks)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)



        if int(list_row):
            if self.page < total_pages:
                self.page += 1
                return self.get_list(url)


if __name__ == '__main__':
    star = datetime.now()
    gk = GkJob()
    gk.start('http://gdit.jobsys.cn/unijob/index.php/wx/jobfair/com_lists?id=70&page_size=10&p=')
    end = datetime.now()
    print('time:', end - star)
