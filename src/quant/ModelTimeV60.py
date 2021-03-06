# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle 

'''
开盘60分钟内V型

'''
class ModelTimeV60:

    def __init__(self, hist_days, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_day, realtime_stock_times):
	try:

#            if TimeUtils.is_after('11:30:00'):
#                return None

	    is_hit = True
	    is_hit = realtime_stock_day.low < realtime_stock_day.op and realtime_stock_day.close > realtime_stock_day.op
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.last_close)			#当前价格高于昨天收盘价
	    is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * realtime_stock_day.last_close)         #均价高于昨日收盘价
	    

	    if is_hit:
		return ('TimeV60-0',)

	except Exception, e:
	    traceback.print_exc()
#	    print jsonpickle.encode(realtime_stock_times_map)

	return None
