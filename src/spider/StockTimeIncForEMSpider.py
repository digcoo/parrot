# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback

from utils.ObjectUtils import *
from utils.HttpUtils import *
from utils.CommonUtils import *
from utils.ParseForEMUtils import *
from utils.EMStockUtils import * 
from dbs.MysqlClient import *
from dbs.GeodeClient import *
from dbs.RedisClient import *
from vo.PlateInfo import *
from vo.PlateDayInfo import *
from dto.DataContainer import *
from analyzer.StockTimeAnalyzer import *

'''
同花顺当日实时交易数据爬取分析
'''
class StockTimeIncForEMSpider:

    def __init__(self, stock_analyzer, symbols, inc_persist, hit_persist, identify):
	self.stock_analyzer = stock_analyzer
	self.symbols = symbols
	self.inc_persist = inc_persist
	self.hit_persist = hit_persist
	self.identify = identify


    def get_all_stocks_realtime_trades(self):
	fail_symbols = []
	hit_list = []
	flag = False
	loop = 0
        for symbol in self.symbols:
	    try:
		loop += 1
		print loop
		LogUtils.info('=================================stock_time_inc_for_em, symbol=%s======================================================\n' % (symbol, ))
#		if not flag and symbol == 'sz002702':
#		    flag = True
		
#		if not flag:
#		    continue

		date_stamp, realtime_time_stock_trades, last_close = EMStockUtils.get_realtime_time_stock_trades(symbol)
		if realtime_time_stock_trades is None:
		    fail_symbols.append(symbol)
		    continue

                if self.stock_analyzer is not None:
                    batch_hit = self.analyze({symbol : realtime_time_stock_trades, 'last_close' : last_close, 'symbol' : symbol, 'today_stamp' : date_stamp})
                    if  batch_hit is not None :
			LogUtils.info('stock_time_hit : ' + jsonpickle.encode(batch_hit))
                        hit_list.append(batch_hit)

		if self.inc_persist:
		    GeodeClient.get_instance().put_stock_time_trades(symbol, date_stamp, realtime_time_stock_trades)

#		LogUtils.info('get_realtime_time_stock_trades, symbol = ' + symbol + ', trades_size = ' + str(len(realtime_time_stock_trades))+ '\n')
	    except Exception, e:
		traceback.print_exc()
		fail_symbols.append(symbol)


	#推荐数据持久存储
	if len(hit_list) > 0 and self.hit_persist:
	    RedisClient.get_instance().put_today_rec(hit_list, self.identify)

	LogUtils.info('stock time recommend stock cnt = ' + str(len(hit_list)))
#	LogUtils.info('stock time recommend stocks = ' + jsonpickle.encode(hit_list))

	LogUtils.info('stock_time_inc_for_ths, fail_symbols_size = ' + str(len(fail_symbols)) + ', fail_symbols = ' + jsonpickle.encode(fail_symbols) + '\n')


    def analyze(self, realtime_stock_times_map):
        try:
            if realtime_stock_times_map is not None:
                return self.stock_analyzer.match(realtime_stock_times_map)
        except Exception, e:
            traceback.print_exc()
        return None


