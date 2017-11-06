# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle 

'''
开盘拉升

'''
class ModelTimeOpenRise:

    def __init__(self, hist_days, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_day, realtime_stock_times):
	try:

#            if TimeUtils.is_after('11:30:00'):
#                return None

	    is_hit = True
	    is_hit = (is_hit) and (realtime_stock_day.low == realtime_stock_day.op)
	    is_hit = (is_hit) and (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)
	    is_hit = (is_hit) and (realtime_stock_day.close > realtime_stock_day.last_close)

	    if is_hit:
		return ('OpenRise-0',)

	except Exception, e:
	    traceback.print_exc()

	return None
