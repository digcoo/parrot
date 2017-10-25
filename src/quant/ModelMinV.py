# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle

'''
1、当日早盘分时下降调整，后V型反转(昨日收红、今日微服高开最佳)
2、当日光头阳线(昨日收绿最佳)
'''
class ModelMinV:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days

    def match(self, realtime_stock_day):

	try:

            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
	    last2_stock_day = BaseStockUtils.pre_stock_day(hist_days, 2, self.todaystamp)

            if last1_stock_day is None or last2_stock_day is None:
                return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)

            last1_max_daily_ma = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)              #昨日日K线
            last0_max_daily_ma = IndicatorUtils.ALL_MA(current_hist_days, TimeUtils.date_add(self.todaystamp, 7))              #今日日K线

	    last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.todaystamp)
            last1_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 1, self.todaystamp)

#            LogUtils.info('last_stock_day=' + json.encode(last1_stock_day))
#            LogUtils.info('realtime_stock_day = ' + json.encode(realtime_stock_day))


	    is_hit = True
#	    is_hit = is_hit & (last1_is_red or last1_change_shadow > 0)				#昨日收红
#            is_hit = is_hit & (realtime_stock_day.op > last1_stock_day.close)                  #高开
            is_hit = is_hit & (realtime_stock_day.low < max(realtime_stock_day.op, last1_stock_day.close))                  #下降调整
            is_hit = is_hit & (realtime_stock_day.low > 0.985 * min(realtime_stock_day.op, last1_stock_day.close))          #小幅调整

#            is_hit = is_hit & (realtime_stock_day.close > 1.004 * last1_stock_day.close)              #当前价高于昨天收盘价,且偏离0轴

#            is_hit = is_hit & (last1_max_daily_ma is not None and last1_stock_day.close > 0.99 * last1_max_daily_ma)           #昨日收盘价接近昨日日K线均线
#            is_hit = is_hit & (last0_max_daily_ma is not None and realtime_stock_day.close > last0_max_daily_ma)           #当前价高于当日日K均线


	    if is_hit:
		return ('MinV-0',)


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

