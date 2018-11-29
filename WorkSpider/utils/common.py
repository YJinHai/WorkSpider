# -*- coding: utf-8 -*-
__author__ = '杨金海'

import hashlib
import re

import pickle
import redis

redis_cli = redis.StrictRedis()


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    #从字符串中提取出数字
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

def real_time_count(key, init):
    if redis_cli.get(key):
        count = pickle.loads(redis_cli.get(key))
        count = count + 1
        count = pickle.dumps(count)
        redis_cli.set(key, count)
    else:
        count = pickle.dumps(init)
        redis_cli.set(key, count)

if __name__ == "__main__":
    print (get_md5("http://www.shixiseng.com".encode("utf-8")))