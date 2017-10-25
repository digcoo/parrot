# encoding=utf8 
from sys import path
#path.append('/home/ubuntu/scripts/gemfire')
path.append('/home/ubuntu/scripts/vo')
#from GemfireClient import *
from gemfire import *
import time
import datetime
from StockDayInfo import *
import jsonpickle
from GeodeClient import *
'''
更改历史last_close

'''

class StockDayLastCloseUpdate:

    def __init__(self):
	self.geode_client = GeodeClient()

    def import_all(self):
#	symbols = self.geode_client.query_all_stock_symbols()
	symbols = ['sh600760','sh600275','sh600390','sh600381','sh600225','sh600721','sh600696','sh600866','sh600817','sh600767','sh600860','sh600675','sh600149','sh600732','sh600680','sh601519','sh601005','sh600793','sh600747','sh600733','sh600725','sh600701','sh600636','sh600581','sh600346','sh600228','sh600145','sz300706','sh600375','sh600540','sh600815','sh600539','sh600710','sh600301','sh600844','sh600339','sh600234','sh600603','sh600877','sh600091','sh600247','sh600179','sh601106','sh600112','sh600608','sh600319','sh600265','sh600847','sh600403','sh600423','sh601558','sh600401','sh600212','sh600306','sh600520','sh600425','sh601918','sh600121','sh600654','sh600556','sh600230','sh600546','sh603106','sh603103','sh603055','sh601086','sh600806','sh600432','sz300705','sz300703','sz300702','sz300654','sz002902','sz002901','sz002900','sh603963','sh603922','sh603619','sh603533','sh603378','sh603367','sh603363','sh603157','sh603136']
	flag = False
	for symbol in symbols:
#	    if symbol == 'sz300365':
#		flag = True
#	    if not flag:
#		continue

	    stock_days = self.geode_client.query_stock_days_latest(symbol, 10000)
	    if stock_days == None:
		break

	    for i in range(len(stock_days) - 1):
		stock_days[i].last_close = stock_days[i+1].close
#		print jsonpickle.encode(stock_days[i])

	    print symbol

	    self.geode_client.add_batch_stock_days(stock_days)


day_import = StockDayLastCloseUpdate()
day_import.import_all()
