# encoding=utf-8

from vo.StockDayInfo import *

class JsonConvert:
    @staticmethod
    def convert_to_dict(obj):
        '''把Object对象转换成Dict对象'''
        tdict = {}
        tdict.update(obj.__dict__)
        return tdict
    
    @staticmethod
    def convert_to_dicts(objs):
        '''把对象列表转换为字典列表'''
        obj_arr = []
        for o in objs:
        #把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr

    @staticmethod
    def class_to_dict(obj):
        '''把对象(支持单个对象、list、set)转换成字典'''
        is_list = obj.__class__ == [].__class__
        is_set = obj.__class__ == set().__class__
        if is_list or is_set:
            obj_arr = []
            for o in obj:
                #把Object对象转换成Dict对象
                dict = {}
                dict.update(o.__dict__)
                obj_arr.append(dict)
            return obj_arr
        else:
            dict = {}
            dict.update(obj.__dict__)
            return dict

'''

stock_days = []



stock_day = StockDayInfo()
stock_day.symbol='sh600100'
stock_day.vol = float('10.01')
stock_days.append(stock_day)

stock_day2 = StockDayInfo()
stock_day2.symbol='sh600100'
stock_day2.vol = float('10.01')
stock_days.append(stock_day2)

print JsonConvert.convert_to_dicts(stock_days)

'''
