# -*- coding: utf-8 -*-
__author__ = '杨金海'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "shixiseng"])
execute(["scrapy", "crawl", "lagou"])