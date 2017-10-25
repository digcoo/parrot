# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle

'''
最后30分钟线实体

'''
class ModelTime30:

    def __init__(self, hist_days, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_day, realtime_stock_times):
	try:

            if not TimeUtils.is_after('14:40:00'):
                return None
	    hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)

	    last1_ma5 = IndicatorUtils.MA(hist_days, 5, self.todaystamp)

	    min30_times = BaseStockUtils.compose_stock_trades_for_minute(realtime_stock_times, 30)
	    min30_times.reverse() 

#	    print 'last_min30 = ' + jsonpickle.encode(min30_times)

	    last_min30 = min30_times[0]

#            current_stock_time = current_hist_times[len(current_hist_times) - 1]
#            min5_max_ma = IndicatorUtils.ALL_MA(min5_times, TimeUtils.date_add(self.todaystamp, 1))
#            min15_max_ma = IndicatorUtils.ALL_MA(min15_times, TimeUtils.date_add(self.todaystamp, 1))

	    is_hit = True
#	    is_hit = is_hit & (realtime_stock_day.op > 0.985 * realtime_stock_day.last_close)
#            is_hit = is_hit & (current_stock_time.close > min5_max_ma)          #大于5分钟MA所有K线
#            is_hit = is_hit & (current_stock_time.close > min15_max_ma)         #大于15分钟MA所有K线
	    is_hit = is_hit & (last_min30.close > 1.0025 * last_min30.op)		#最后30分钟线
#	    is_hit = is_hit & (realtime_stock_day.close > 1.005 * realtime_stock_day.op and realtime_stock_day.close < 1.02 * realtime_stock_day.op)	#收红
	    is_hit = is_hit & (realtime_stock_day.close > 1.005 * realtime_stock_day.op)
	    is_hit = is_hit & (realtime_stock_day.close > last1_ma5)			#收于ma5上

#	    print 'ma5 = ' + str(last1_ma5) + ', todaystamp = ' + TimeUtils.timestamp2datestring(self.todaystamp)
	    if is_hit:
		return ('Time30-0',)

	except Exception, e:
	    traceback.print_exc()
	    print jsonpickle.encode(realtime_stock_day)
	    print jsonpickle.encode(realtime_stock_times)

	return None

