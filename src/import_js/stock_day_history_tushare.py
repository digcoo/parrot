import tushare as ts
from StockInfo import *
from ParseUtil import *
from GeodeClient import *

import cPickle as pickle


class StockDayHistoryTushare:

    def __init__(self):
        self.geode_client = GeodeClient()


    def get_stock_days_history(self, symbol):
        try:
            code = symbol[2 : len(symbol)]
            stock_days_history_framedata = ts.get_hist_data(code)
            stock_days = ParseUtil.compose_stock_days(symbol, stock_days_history_framedata)
#	    print pickle.dumps(stock_days[0])

        except Exception, e:
            print e
        return ''


    def get_allstocks_day(self):
        try:
            symbols = self.geode_client.query_all_stock_symbols()
	    for symbol in symbols:
		code = symbol[2 : len(symbol)]
		stock_days_history_framedata = ts.get_hist_data(code)
		stock_days = ParseUtil.compose_stock_days(symbol, stock_days_history_framedata)
		print len(stock_days)
		self.add_stock_days_page(stock_days)
		
        except Exception, e:
            print e

    def add_stock_days_page(self, stock_days):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(stock_days) else len(stock_days)
        temp_stock_days = stock_days[start : end]
        while(len(temp_stock_days) > 0):
	    self.geode_client.put_stocks_day(temp_stock_days)

	    page += 1	    
	    start = (page -1) * size
            end = page*size if page * size < len(stock_days) else len(stock_days)
            temp_stock_days = stock_days[start : end]


spider = StockDayHistoryTushare()
#spider.get_allstocks_day()
spider.get_stock_days_history('sh601101')






