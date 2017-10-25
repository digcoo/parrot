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
from SinaStockUtils import *
from CommonUtils import *
from WeightUtils import *
from IndicatorUtils import *
from TimeUtils import *
from LogUtils import *

'''
高于日K线但低于周K线
'''
class ModelDNWMA:

    def __init__(self, hist_days, hist_weeks, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
        self.cache_hist_weeks = hist_weeks 

    def match(self, realtime_stock_day):
	try:

	    hist_days = self.cache_hist_days[realtime_stock_day.symbol]
	    hist_weeks = self.cache_hist_weeks[realtime_stock_day.symbol]
	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
	    if last1_stock_day is None:
		return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)

            last0_stock_week = hist_weeks[0] if (len(hist_weeks) > 0 and TimeUtils.is_same_week_with_datestamp(hist_weeks[0].day, self.todaystamp)) else None      #本周周K线(不包括当天)
	    last1_max_daily_ma = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)              #昨日日K线
	    last0_max_daily_ma = IndicatorUtils.ALL_MA(current_hist_days, TimeUtils.date_add(self.todaystamp, 7))              #今日日K线
	    last1_max_week_ma = IndicatorUtils.ALL_MA(hist_weeks, self.todaystamp)		#上周周K线
	    last0_max_week_ma = IndicatorUtils.ALL_MA(hist_weeks, TimeUtils.date_add(self.todaystamp, 7))              #本周周K线

	    is_hit = True

            is_hit = is_hit & (last0_stock_week is None or realtime_stock_day.close > last0_stock_week.op)      #本周周K线收红

	    is_hit = is_hit & (realtime_stock_day.close > last1_max_daily_ma)					#当前价格高于昨日K均线
            is_hit = is_hit & (realtime_stock_day.close > last0_max_daily_ma)                                   #当前价格高于昨日K均线
            is_hit = is_hit & (realtime_stock_day.close < last1_max_week_ma)                                   #当前价格高于昨日K均线
            is_hit = is_hit & (realtime_stock_day.close < last0_max_week_ma)                                   #当前价格高于昨日K均线

            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)

            if is_hit:
		return ('DNWMA-0', )

	except Exception, e:
	    traceback.print_exc()

	return None


