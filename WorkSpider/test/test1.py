# -*- coding: utf-8 -*-
import base64
import re
import os

import requests
from fontTools.ttLib import TTFont

__author__ = '杨金海'


class MaoYan(object):
    def __init__(self):
        self.url = 'https://www.shixiseng.com/intern/inn_ykdw1q4ok88d'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        self.font = ''
        self.gly_list = ''
        self.gly_map = ''

    # 发送请求获得响应
    def get_html(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    # 创建 self.font 属性
    def create_font(self, font_file):
        fontdata = base64.b64decode(font_file)
        file = open('./font.ttf', 'wb')
        file.write(fontdata)
        file.close()
        self.font = TTFont('./font.ttf')
        # 保存xml方便手动核对
        # font.saveXML('./font.xml')

        # 获取 GlyphOrder 节点
        self.gly_list = self.font.getGlyphOrder()
        # 前两个不是需要的值，截掉
        self.gly_list = self.gly_list[2:]
        self.gly_map = self.font.getBestCmap()

    # 把获取到的数据用字体对应起来，得到真实数据
    def modify_data(self, data):

        for k, v in self.gly_map.items():
            s = str(hex(k)).replace('0x', '&#x')
            if s in data:
                # print(hex(k),s,v,gly_list.index(v))
                data = data.replace(s, str(self.gly_list.index(v)))
        print(data)
        return data

    def start_crawl(self):
        html = self.get_html(self.url).decode('utf-8')

        # 正则匹配字体文件
        font_file = re.findall(r"src: url\(\"data:application/octet-stream;base64,(.*?)\"\)", html)[0]
        self.create_font(font_file)

        # 正则匹配星级
        star = re.findall(r'<div class="job_detail cutom_font">(.*?)</div>', html)[0]
        print(star)
        star = self.modify_data(star)


if __name__ == '__main__':
    maoyan = MaoYan()
    maoyan.start_crawl()
