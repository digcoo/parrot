# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle

'''
'''
class ModelTimeMA:

    def __init__(self, hist_times, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_times = hist_times

    def match(self, realtime_stock_times_map):
	try:

            symbol = realtime_stock_times_map.get('symbol')
            last_close = realtime_stock_times_map.get('last_close')
            hist_times = self.cache_hist_times.get(symbol)
	    current_hist_times = BaseStockUtils.compose_realtime_stock_times(hist_times, realtime_stock_times_map.values()[0])

	    min5_times = BaseStockUtils.compose_stock_trades_for_minute(current_hist_times, 5)
	    min5_times.reverse() 
	    min15_times = BaseStockUtils.compose_stock_trades_for_minute(current_hist_times, 15)
	    min15_times.reverse()
#	    min60_times = BaseStockUtils.compose_stock_trades(current_hist_times, 60)

	    current_stock_time = current_hist_times[len(current_hist_times) - 1]

#	    print 'current_stock_time = ' + jsonpickle.encode(current_stock_time)

	    min5_max_ma = IndicatorUtils.ALL_MA(min5_times, TimeUtils.date_add(self.todaystamp, 1))
	    min15_max_ma = IndicatorUtils.ALL_MA(min15_times, TimeUtils.date_add(self.todaystamp, 1))


#	    LogUtils.info('min5_max_ma = ' + str(min5_max_ma))
#	    LogUtils.info('min15_max_ma = ' + str(min15_max_ma))

	    is_hit = True
	    is_hit = is_hit & (current_stock_time.close > min5_max_ma)		#大于5分钟MA所有K线
	    is_hit = is_hit & (current_stock_time.close > min15_max_ma)		#大于15分钟MA所有K线

	    if is_hit:
		return ('TimeMA-0',)

	except Exception, e:
	    traceback.print_exc()
#	    print json.encode(self.cache_hist_days[realtime_stock_day.symbol])

	return None

if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sz002728'

    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 10)


    hist_symbols_days[symbol] = latest_days
    model_close = ModelMinV(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)

