# -*- coding: utf-8 -*-
import threading
from multiprocessing import Process
from time import sleep

__author__ = '杨金海'

import requests
import asyncio
import pymysql

from proxybroker import Broker

conn = pymysql.connect(host="127.0.0.1", user="root", passwd="root", db="workspider", charset="utf8")
cursor = conn.cursor()


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


class CrawlProxy(Process):
    def __init__(self, crawl_num):
        super().__init__()
        self.start_crawl(crawl_num)
        # new_loop.call_soon_threadsafe(self.start_crawl, 25)

    @asyncio.coroutine
    async def save(self, proxies):
        """Save proxies to a file."""
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            print('Found proxy: %s' % proxy)
            proto = 'https' if 'HTTPS' in proxy.types else 'http'
            row = '%s://%s:%d' % (proto, proxy.host, proxy.port)
            print(row)
            cursor.execute(
                "insert ignore proxy_ip(ip) VALUES('{0}')".format(row)
            )

            conn.commit()

    def start_crawl(self, crawl_num):
        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=crawl_num),
                               self.save(proxies))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, proxy_url):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)

        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(proxy_url)
            return False
        else:
            code = response.status_code
            if 200 <= code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(proxy_url)
                return False

    def get_ip_number(self):
        # 判断数据是否有足够的ip
        random_sql = """
                              SELECT COUNT(*) FROM proxy_ip
                            """
        cursor.execute(random_sql)
        for number in cursor.fetchall():
            return number[0]


    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        number = self.get_ip_number()
        if 20 > number:
            # 这里存在着进进程间通信的竞争的可能性，这是不完善的
            crawl_proxy = CrawlProxy(100)
            crawl_proxy.start()

        random_sql = """
              SELECT ip FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
            """
        cursor.execute(random_sql)
        for ip in cursor.fetchall():
            judge_re = self.judge_ip(ip[0])
            if judge_re:
                return ip[0]
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    # crawl_ips()
    get_ip = GetIP()
    get_ip.get_random_ip()

