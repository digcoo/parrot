# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle 

'''
分时线节节攀升

'''
class ModelTimeMin:

    def __init__(self, hist_days, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_day, realtime_stock_times):
	try:

            if realtime_stock_day.symbol == 'sh603689':
                LogUtils.info('ModelTimeV60 realtime_stock_times : ' + jsonpickle.encode(realtime_stock_times) + '\n\n')

	    if len(realtime_stock_times) < 2:
		return None

	    min_times	= realtime_stock_times
	    min5_times	= BaseStockUtils.compose_stock_trades_for_sina_minute(realtime_stock_times, 5)
	    min15_times = BaseStockUtils.compose_stock_trades_for_sina_minute(realtime_stock_times, 15)
	    min30_times = BaseStockUtils.compose_stock_trades_for_sina_minute(realtime_stock_times, 30)
	    min60_times = BaseStockUtils.compose_stock_trades_for_sina_minute(realtime_stock_times, 60)

            if realtime_stock_day.symbol == 'sh603689':
                LogUtils.info('ModelTimeMin  min5_times : ' + jsonpickle.encode(min5_times) + '\n\n')
		LogUtils.info('ModelTimeMin  min15_times : ' + jsonpickle.encode(min15_times) + '\n\n')
		LogUtils.info('ModelTimeMin  min30_times : ' + jsonpickle.encode(min30_times) + '\n\n')
		LogUtils.info('ModelTimeMin  min60_times : ' + jsonpickle.encode(min60_times) + '\n\n')



	    is_hit = True

            #5分钟策略
            if len(min5_times) <= 1:            #5分钟内
		is_hit = min_times[len(min_times) - 1].close > max([min_time.close for min_time in min_times[:len(min_times) - 1]]) and min_times[len(min_times) - 1].close > realtime_stock_day.last_close
            elif len(min5_times) <= 3:          #15分钟内
                is_hit = min5_times[len(min5_times) - 1].high > max([min5_time.high for min5_time in min5_times[:len(min5_times) - 1]]) and min5_times[len(min5_times) - 1].close > realtime_stock_day.last_close
#		print '5-15:' + str(is_hit)
            elif len(min5_times) <= 6:          #15-30分钟内
                is_hit = min15_times[1].high > min15_times[0].high and min15_times[1].close > realtime_stock_day.last_close
#		print '15-30:' + str(is_hit)
            elif len(min5_times) <= 12:         #30-60分钟内
                is_hit = min30_times[1].high > min30_times[0].high and min30_times[1].close > realtime_stock_day.last_close
#		print '30-60:' + str(is_hit)
            else:                               #60分钟以上
		is_hit = min60_times[len(min60_times) - 1].high > min60_times[0].high and min60_times[len(min60_times) - 1].close > max(realtime_stock_day.last_close, realtime_stock_day.op)
#                is_hit = min60_times[len(min60_times)-1].close > max(realtime_stock_day.last_close, realtime_stock_day.money / realtime_stock_day.vol)
#		print '60+:' + str(is_hit)

	    if is_hit:
		return ('TimeMin-0',)

	except Exception, e:
	    traceback.print_exc()
#	    print jsonpickle.encode(realtime_stock_times_map)

	return None
