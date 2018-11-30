# -*- coding: utf-8 -*-
__author__ = '杨金海'


class A(object):

    def __init__(self, parms):
        self.parms = parms
        self.print_dicts(**parms)

    def print_dicts(self, **parms):
        print(parms['NAME'], parms['AGE'])

    # 类方法（不需要实例化类就可以被类本身调用）
    @classmethod
    def from_settings(cls, g_dict):  # cls : 表示没被实例化的类本身

        return cls(g_dict) # 实例化


