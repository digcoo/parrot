#encoding=utf-8

import traceback
import jsonpickle
import sys
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/vo')
path.append('/home/ubuntu/scripts/utils')
from StockInfo import *
from ParseUtil import *
from GeodeClient import *
from MyMongoClient import *
from TimeUtils import *
from LogUtils import *


class TransformStockTime:

    def __init__(self):
	self.geode_client = GeodeClient.get_instance()
	self.mongo_client = MyMongoClient.get_instance()


    #保留stock_time4天数据
    def transform_all_stock_times(self):
	symbols = self.geode_client.query_all_stock_symbols()
	index = 0
        for symbol in symbols:
	    index += 1
	    LogUtils.info('transform_all_stock_times, symbol = ' + symbol + ', index = ' + str(index))
	    ids = []
	    ids.append(symbol)
            stock_times_map = self.geode_client.query_stock_time_trades_map_by_idlist(ids)
	    if stock_times_map is None or len(stock_times_map) == 0:
		continue
	    stock_times_map = stock_times_map.get(symbol)
	    days = stock_times_map.keys()
	    days = ParseUtil.transfer_unicodes_ints(days)
	    days = sorted(days)
	    latest_day = days[len(days) - 1]
	    latest_day_times = stock_times_map.get(unicode(latest_day))
	    self.geode_client.put_stock_time_trades(symbol, latest_day, latest_day_times)
#	    break


if __name__ == '__main__':
    transform_util =  TransformStockTime()
    transform_util.transform_all_stock_times()
