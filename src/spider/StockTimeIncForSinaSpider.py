# encoding=utf8  
import time
import urllib2
import jsonpickle as json
import traceback
from utils.HttpUtils import *
from vo.StockInfo import *
from utils.ParseForSinaUtils import *
from dbs.GeodeClient import *
from dbs.RedisClient import *
from utils.CommonUtils import *
from utils.LogUtils import *
from utils.SinaStockUtils import *

class StockTimeIncForSinaSpider:

    def __init__(self, stock_analyzer, symbols, inc_persist, hit_persist, identify):
	self.stock_single_url = 'http://hq.sinajs.cn/list={0}'
	self.stock_analyzer = stock_analyzer
	self.symbols = symbols
	self.inc_persist = inc_persist
	self.hit_persist = hit_persist
	self.identify = identify
	self.realtime_stock_times_map = {}
	LogUtils.info('stock_day_inc_for_sina_spider init finish...')


    def get_all_stocks_realtime_trades(self):
	try:
	    hit_list = []
	    fail_symbols = []
	    page = 1
	    size = 100
	    start = (page -1) * size
	    end = page*size if page * size < len(self.symbols) else len(self.symbols)
	    temp_symbols = self.symbols[start : end]
	    while(len(temp_symbols) > 0):
#		LogUtils.info('=================================stock_time_inc_for_sina, symbol=%s, page=%s=======================================\n' % (temp_symbols, page))
		stocks_day = SinaStockUtils.get_current_stock_days(temp_symbols)

		tmp_fail_symbols = self.filter_fail_symbols(temp_symbols, stocks_day)
		if tmp_fail_symbols is not None:
		    fail_symbols.extend(tmp_fail_symbols)

		for realtime_stock_day in stocks_day:
		    realtime_time_stock_trades= ParseForSinaUtils.compose_realtime_stock_trades(self.realtime_stock_times_map, realtime_stock_day)
		    self.realtime_stock_times_map[realtime_stock_day.symbol] = realtime_time_stock_trades

		    date_stamp = TimeUtils.timestamp2datestamp(realtime_stock_day.day)

		    if self.stock_analyzer is not None:
#			realtime_stock_day = BaseStockUtils.compose_realtime_stock_day_from_time_trades(realtime_time_stock_trades, symbol=symbol, last_close=last_close, today_stamp=date_stamp)
			batch_hit = self.analyze(realtime_time_stock_trades, realtime_stock_day)
			if  batch_hit is not None :
			    LogUtils.info('stock_time_hit : ' + jsonpickle.encode(batch_hit))
			    hit_list.append(batch_hit)

		    #日线数据持久存储
		    if self.inc_persist:
 			GeodeClient.get_instance().put_stock_time_trades(symbol, date_stamp, realtime_time_stock_trades)
		
		page += 1
                start = (page -1) * size
                end = page*size if page * size < len(self.symbols) else len(self.symbols)
                temp_symbols = self.symbols[start : end]
	    
	    LogUtils.info('stock day recommend stock cnt = ' + str(len(hit_list)))

	except Exception, e:
	    traceback.print_exc()


        #推荐数据持久存储
        if len(hit_list) > 0 and self.hit_persist:
            RedisClient.get_instance().put_today_rec(hit_list, self.identify)

        LogUtils.info('stock time recommend stock cnt = ' + str(len(hit_list)))

        LogUtils.info('stock_time_inc_for_sina, fail_symbols_size = ' + str(len(fail_symbols)) + ', fail_symbols = ' + jsonpickle.encode(fail_symbols) + '\n')




    def analyze(self, realtime_stock_times, realtime_stock_day):
        try:
            if realtime_stock_times is not None and realtime_stock_day is not None:
                return self.stock_analyzer.match(realtime_stock_times, realtime_stock_day)
        except Exception, e:
            traceback.print_exc()
        return None


    def filter_fail_symbols(self, source_symbols, collected_realtime_trades):
	market_symbols = []
	if collected_realtime_trades is not None and len(collected_realtime_trades) > 0:
	    fail_symbols = []
	    for realtime_stock_day in collected_realtime_trades:
		market_symbols.append(realtime_stock_day.symbol)
	    for source_symbol in source_symbols:
		if source_symbol not in market_symbols:
		    fail_symbols.append(source_symbol)
	    return fail_symbols
