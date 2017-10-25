# encoding=utf8 
from sys import path
#path.append('/home/ubuntu/scripts/gemfire')

#from GemfireClient import *
from gemfire import *
import time
import datetime
from StockDayInfo import *
import jsonpickle

#将旧数据类型转换后导入新的region

class StockDayImport:

    def __init__(self):
        self.client = GemfireClient(hostname = '52.80.22.16', port = '8080')

    def query_all_stock_symbols(self):
        stock_repo = self.client.create_repository('stock')
        stock_region = stock_repo.get_region()
        return stock_region.keys()

    def query_stock_days_by_symbol(self, symbol):
	stock_repo = self.client.create_repository('stock-day')
	paras = [symbol]
	paras_types = ['String']
	stock_days = self.client.my_query("select_stock_days_by_symbol", paras, paras_types)
	return stock_days

    def put_target_stocks_day(self, stocks_day):
	stock_day_repo = self.client.create_repository('stock-day-final')
	stock_day_repo.save(stocks_day)

    def query_source_stocks_day(self, page):
	size = 50
	start = (page - 1) * size
	paras = [start, size]
	source_data = self.client.run_query('select_stock_day_page', paras)
	return source_data

    def import_all(self):
	stock_day_repo = self.client.create_repository('stock-day-final')
	symbols = self.query_all_stock_symbols()
	for symbol in symbols:
	    stock_days = self.query_stock_days_by_symbol(symbol)
	    if stock_days == None:
		break

	    for stock_day in stock_days:
		jvalue = jsonpickle.encode(stock_day)
		target_stock_day = self.convert_data_types(stock_day)
#		print jsonpickle.encode(target_stock_day)
		stock_day_repo.save(target_stock_day)

    def convert_data_types(self, stock_day):
	try:
	    target_stock_day = StockDayInfo()
            target_stock_day.id = stock_day.id.replace('-', '')
            target_stock_day.day = int(time.mktime(time.strptime(stock_day.day[0:10], "%Y-%m-%d")))
            target_stock_day.symbol = stock_day.symbol   #代码symbol
            target_stock_day.op = float(stock_day.op)   #开盘价
            target_stock_day.close = float(stock_day.close)   #当前价
            target_stock_day.high = float(stock_day.high)   #最高价
            target_stock_day.low = float(stock_day.low)   #最低价
            target_stock_day.buy1 = float(stock_day.buy1)   #买一价
            target_stock_day.sell1 = float(stock_day.sell1)   #卖一价
            target_stock_day.vol = float(stock_day.vol)   #成交量(股)
            target_stock_day.money = float(stock_day.money)   #成交总金额(元)
            target_stock_day.buy1_vol = float(stock_day.buy1_vol)   #买一量(股)
            target_stock_day.sell1_vol = float(stock_day.sell1_vol)   #卖一量(股)
#	    print jsonpickle.encode(target_stock_day)
	    return target_stock_day
	except Exception, e:
	    print '-------------------------------------error------------------------------------'
	    print e

day_import = StockDayImport()
day_import.import_all()

#client = GemfireClient(hostname = '52.80.22.16', port = '8080')
#params = ['sz300167']
#params_types = ['String']
#ret = client.my_query('select_stock_days_by_symbol', params, params_types)

#print len(ret)
