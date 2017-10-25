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

'''
1、昨日收于低于日K线
2、今日高于日K线
'''
class ModelCrossDMA:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days

    def match(self, realtime_stock_day):

	try:

            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)

            last1_max_daily_ma = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)              #昨日日K线
            last0_max_daily_ma = IndicatorUtils.ALL_MA(current_hist_days, TimeUtils.date_add(self.todaystamp, 7))              #今日日K线

	    is_hit = True
#	    is_hit = is_hit & (last1_max_daily_ma is not None and realtime_stock_day.close > 1.002 * last1_max_daily_ma)     #当前价高于昨日MA5
#            is_hit = is_hit & (realtime_stock_day.close > 1.004 * last1_stock_day.close)              #当前价高于昨天收盘价,且偏离0轴
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)              #当前价高于开盘价
#	    is_hit = is_hit & (BaseStockUtils.lower_shadow(realtime_stock_day) < 0.015)                         #下影线

            is_hit = is_hit & (last1_max_daily_ma is not None and last1_stock_day.close < last1_max_daily_ma)           #昨日收盘价低于昨日日K线均线

            is_hit = is_hit & (last0_max_daily_ma is not None and realtime_stock_day.close > last0_max_daily_ma)           #当前价高于当日日K均线

            is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * last1_stock_day.close)         #均价高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.994 * last1_stock_day.close)         #当前价格高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.996 * realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价


	    if is_hit:
		return ('CDMA-0',)


	except Exception, e:
	    traceback.print_exc()
#	    print json.encode(self.cache_hist_days[realtime_stock_day.symbol])

	return None
