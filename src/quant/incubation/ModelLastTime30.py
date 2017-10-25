# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/vo')
import time
import traceback
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from CommonUtils import *
from IndicatorUtils import *
from LogUtils import *

'''
最后30分钟线实体

'''
class ModelLastTime30:

    def __init__(self, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_times_map):
	try:
	    symbol = realtime_stock_times_map.get('symbol')
	    last_close = realtime_stock_times_map.get('last_close')
	    hist_times = self.cache_hist_times.get(symbol)
	  
	    realtime_stock_times = realtime_stock_times_map.get(symbol)
	    realtime_stock_day = BaseStockUtils.compose_realtime_stock_day_from_time_trades(realtime_stock_times)
	    current_hist_times = BaseStockUtils.compose_realtime_stock_times(hist_times, realtime_stock_times)

	    last1_min30_times = BaseStockUtils.compose_stock_trades_for_minute(hist_times, 30)
	    last1_min30_times.reverse() 

#	    print jsonpickle.encode(last1_min30_times[0])

	    if last1_min30_times[0].day > self.todaystamp:
		last1_min30_times = last1_min30_times[9:]

	    last1_min30 = last1_min30_times[0]          #昨日最后30min

#	    print jsonpickle.encode(last1_min30)

	    is_hit = True
#            is_hit = is_hit & (current_stock_time.close > min5_max_ma)          #大于5分钟MA所有K线
#            is_hit = is_hit & (current_stock_time.close > min15_max_ma)         #大于15分钟MA所有K线
	    is_hit = is_hit & (last1_min30.close > 1.0025 * last1_min30.op)		#最后30分钟线

	    if is_hit:
		return ('LTime30-0',)

	except Exception, e:
	    traceback.print_exc()
	    print jsonpickle.encode(realtime_stock_times_map)

	return None

