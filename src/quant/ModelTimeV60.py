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

#            if TimeUtils.is_after('10:30:00'):
#                return None

	    is_hit = True
	    is_hit = realtime_stock_day.low < realtime_stock_day.op and realtime_stock_day.close > realtime_stock_day.op

	    if is_hit:
		return ('TimeV60-0',)

	except Exception, e:
	    traceback.print_exc()
#	    print jsonpickle.encode(realtime_stock_times_map)

	return None
