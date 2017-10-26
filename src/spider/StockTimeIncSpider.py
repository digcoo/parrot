# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback

from utils.ObjectUtils import *
from utils.HttpUtils import *
from utils.CommonUtils import *
from utils.ParseForThsUtils import *
from utils.ThsStockUtils import * 
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
class StockTimeIncSpider:

    def __init__(self, stock_analyzer, symbols, inc_persist, hit_persist, identify):
        self.stock_timely_realtime_url = 'http://d.10jqka.com.cn/v6/time/hs_{0}/today.js'		#code
        self.stock_detail_url = 'http://stockpage.10jqka.com.cn/{0}/'                   #code(stock.id[2:])
	self.stock_analyzer = stock_analyzer
	self.symbols = symbols
	self.inc_persist = inc_persist
	self.hit_persist = hit_persist
	self.identify = identify


    def get_all_stocks_realtime_trades(self):
	fail_symbols = []
	hit_list = []
        for symbol in self.symbols:
	    try:
#		if symbol != 'sz002909':
#		    continue
#		LogUtils.info('=================================stock_time_inc_for_ths, symbol=%s======================================================\n' % (symbol, ))
		date_stamp, realtime_time_stock_trades, last_close = ThsStockUtils.get_realtime_time_stock_trades(symbol)
		if realtime_time_stock_trades is None:
		    fail_symbols.append(symbol)
		    continue

                if self.stock_analyzer is not None:
                    batch_hit = self.analyze({symbol : realtime_time_stock_trades, 'last_close' : last_close, 'symbol' : symbol, 'today_stamp' : date_stamp})
                    if  batch_hit is not None :
#			LogUtils.info('stock_time_hit : ' + jsonpickle.encode(batch_hit))
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



if __name__ == '__main__':
    symbols = GeodeClient.get_instance().query_all_stock_symbols()
   
    symbols = CommonUtils.filter_symbols(symbols)

    symbols = list(filter(lambda x: x == 'sz002117', symbols))

    data_container = DataContainer()

    stock_analyzer = StockTimeAnalyzer(symbols, TimeUtils.get_current_datestamp(), data_container)

    spider = StockTimeIncSpider(stock_analyzer = stock_analyzer, symbols = symbols, inc_persist = False, hit_persist = True, identify='time-1-0')

    spider.get_all_stocks_realtime_trades()

