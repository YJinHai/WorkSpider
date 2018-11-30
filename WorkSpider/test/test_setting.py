# -*- coding: utf-8 -*-
__author__ = '杨金海'

# 注册中间件
DICTS = [
    'test2.A'
]

NAME = 'YangJiHai' # 全局配置变量
AGE = '20'

# settings文件与中间件交互的处理，为了简便代码放在这里演示
for test in DICTS:
    m, c = test.rsplit('.', 1)  # 反向分割取得类名
    m = __import__(m)  # 导入模块
    if hasattr(m, c):  # 判断模块中是否存在该字符串属性
        target_class = getattr(m, c)  # 获取该属性的引用
        if hasattr(target_class, 'from_settings'):  # 获取inp的引用
            target_func = getattr(target_class, 'from_settings')
            g = globals() # 获取全局变量返回字典类型
            target_func(g)  # 执行

