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
高于月K选股
'''
class ModelMonthMA:

    def __init__(self, hist_days, hist_weeks, hist_months, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
        self.cache_hist_weeks = hist_weeks
	self.cache_hist_months = hist_months

    def match(self, realtime_stock_day):
	try:

#	    hist_days = self.cache_hist_days[realtime_stock_day.symbol]
#	    hist_weeks = self.cache_hist_weeks[realtime_stock_day.symbol]
	    hist_months = self.cache_hist_months[realtime_stock_day.symbol]
	    last0_stock_month = hist_months[0] if (len(hist_months) > 0 and TimeUtils.is_same_month_with_datestamp(hist_months[0].day, self.todaystamp)) else None
#	    if last1_stock_day is None:
#		return None

#            current_hist_days = hist_days[:]
#            if realtime_stock_day.day > hist_days[0].day:
#                current_hist_days.insert(0, realtime_hist_day)

#	    last1_max_daily_ma = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)              #昨日日K线
#	    last0_max_daily_ma = IndicatorUtils.ALL_MA(current_hist_days, TimeUtils.date_add(self.todaystamp, 7))              #今日日K线
#	    last1_max_week_ma = IndicatorUtils.ALL_MA(hist_weeks, self.todaystamp)		#上周周K线
#	    last0_max_week_ma = IndicatorUtils.ALL_MA(hist_weeks, TimeUtils.date_add(self.todaystamp, 7))              #本周周K线
	    last0_max_month_ma = IndicatorUtils.ALL_MA(hist_months, TimeUtils.date_add(self.todaystamp, 31))              #本月月K线

	    is_hit = True

	    is_hit = is_hit & (last0_stock_month is None or realtime_stock_day.close > last0_stock_month.op)			#本月月K线收红	
            is_hit = is_hit & (realtime_stock_day.close > last0_max_month_ma)                                   #当前价格高于当前月K均线（不包括当天）

#            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价
#	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)

            if is_hit:
		return ('MonthMA-0', )

	except Exception, e:
	    traceback.print_exc()

	return None


