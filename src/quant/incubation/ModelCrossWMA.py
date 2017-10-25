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
大比率突破周线
'''
class ModelCrossWMA:

    def __init__(self, hist_days, hist_weeks, hist_months, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
        self.cache_hist_weeks = hist_weeks 
	self.cache_hist_months = hist_months

    def match(self, realtime_stock_day):
	try:

            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            hist_weeks = self.cache_hist_weeks[realtime_stock_day.symbol]
            hist_months = self.cache_hist_months[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

            #封装当天数据
            current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)
            #封装本周数据，更新本周指标
            current_hist_weeks = BaseStockUtils.compose_realtime_stock_weeks(hist_weeks, realtime_stock_day)


            last1_max_week_ma = IndicatorUtils.ALL_MA(hist_weeks, self.todaystamp)              #上周周K线
            last0_max_week_ma = IndicatorUtils.ALL_MA(current_hist_weeks, TimeUtils.date_add(self.todaystamp, 7))              #本周周K


            last1_stock_week = current_hist_weeks[1] if len(current_hist_weeks) > 1 else None            #上周收盘周K线
            last0_stock_week = current_hist_weeks[0]    #本周收盘K线
	
            is_hit = True
	    is_hit = is_hit & (last1_stock_week is not None and last1_stock_week.close < last1_stock_week.op)			   #上周收绿
            is_hit = is_hit & (last0_stock_week.close > 1.02 * last0_stock_week.op)                #周线收红
	    is_hit = is_hit & (realtime_stock_day.close > last0_max_week_ma)			   #周线上
	    
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)


            if is_hit:
		return ('CWMA-0', )

	except Exception, e:
	    traceback.print_exc()
	    LogUtils.info('exception data..' + jsonpickle.encode(realtime_stock_day))

	return None


