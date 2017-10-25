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


class TransferStockTime2Mongo:

    def __init__(self):
	self.geode_client = GeodeClient.get_instance()
	self.mongo_client = MyMongoClient.get_instance()

    #将所有的分时数据导入mongo
    def export_all_stock_times(self):
	symbols = self.geode_client.query_all_stock_symbols()
        for symbol in symbols:
	    ids = []
	    ids.append(symbol)
            stock_times_map = self.geode_client.query_stock_time_trades_map_by_idlist(ids)
	    stock_times_map = ParseUtil.compose_stock_times_from_daytimes_map(stock_times_map)
	    if stock_times_map.get(symbol) is not None and len(stock_times_map.get(symbol)) > 0:
		stock_times = stock_times_map.get(symbol)
	        self.mongo_client.add_stock_times(symbol, stock_times)

    #将最新一天的分时的数据导入mongo   
    def export_latest_stock_times(self):
        symbols = self.geode_client.query_all_stock_symbols()
        for symbol in symbols:
            ids = []
            ids.append(symbol)
            stock_times_map = self.geode_client.query_stock_time_trades_map_by_idlist(ids)
	    if stock_times_map is not None and stock_times_map.get(symbol) is not None:
                days = stock_times_map.get(symbol).keys()
                latest_day = max(days)
                stock_times = stock_times_map.get(symbol).get(latest_day)
#	        print jsonpickle.encode(stock_times)
                self.mongo_client.add_stock_times(symbol, stock_times)



    #为stock-min-final批量创建索引
    def create_indexs(self):
	symbols = self.geode_client.query_all_stock_symbols()
	for symbol in symbols:
	    self.mongo_client.create_index(symbol)

if __name__ == '__main__':
    transfer_util =  TransferStockTime2Mongo()
#   transfer_util.export_all_stock_times()
#    transfer_util.create_indexs()
    transfer_util.export_latest_stock_times()
