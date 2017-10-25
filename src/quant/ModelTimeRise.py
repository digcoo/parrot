# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle 

'''
分时线节节攀升

'''
class ModelTimeRise:

    def __init__(self, hist_days, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_day, realtime_stock_times):
	try:

	    min15_times = BaseStockUtils.compose_stock_trades_for_minute(realtime_stock_times, 15)
	    min30_times = BaseStockUtils.compose_stock_trades_for_minute(realtime_stock_times, 30)
	    min60_times = BaseStockUtils.compose_stock_trades_for_minute(realtime_stock_times, 60)

	    is_hit = True
	    is_hit_min15 = len(min15_times) > 1 and min15_times[1].high > min15_times[0].high and min15_times[1].close > realtime_stock_day.last_close		#15分钟线
	    is_hit_min30 = len(min30_times) > 1 and min30_times[1].high > min30_times[0].high and min30_times[1].close > realtime_stock_day.last_close               #30分钟线
#	    is_hit_min60 = len(min60_times) > 1 and self.max_stock_high(min60_times[1:]) > min30_times[0].high and min60_times[len(min60_times)-1].close > max(realtime_stock_day.last_close, realtime_stock_day.money / realtime_stock_day.vol)               #60分钟线

#	    print is_hit
#	    print 'min15_times : ' + jsonpickle.encode(min15_times)
#	    print 'min30_times : ' + jsonpickle.encode(min30_times)
#	    print 'min60_times : ' + jsonpickle.encode(min60_times)

	    is_hit = is_hit & (is_hit_min15 or is_hit_min30)

	    if len(min60_times) > 1:			#如果时间超过10：30分，则以当前价格超过早盘1小时高点
		is_hit_min60 = True
		is_hit_min60 = is_hit_min60 & (self.max_stock_high(min60_times[1:]) > min60_times[0].high)		#开盘后1小时突破前期高点
		is_hit_min60 = is_hit_min60 & (min60_times[len(min60_times)-1].close > max(realtime_stock_day.last_close, realtime_stock_day.money / realtime_stock_day.vol))	#收盘价高于昨日且高于均价

		#如果前1小时符合，则后必须符合
		if is_hit:
		    is_hit = is_hit & (is_hit_min60)
		else:
		    is_hit = is_hit or is_hit_min60

	    if is_hit:
		return ('TimeRise-0',)

	except Exception, e:
	    traceback.print_exc()
#	    print jsonpickle.encode(realtime_stock_times_map)

	return None

    def max_stock_high(self, stock_times):
	highs = [stock_time.high for stock_time in stock_times]
	return max(highs)
