# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle as json

'''
上周大比率突破周线
'''
class ModelCLWMMA:

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
            #封装本月数据，更新本月指标
            current_hist_months = BaseStockUtils.compose_realtime_stock_months(hist_months, realtime_stock_day)



            last1_max_week_ma = IndicatorUtils.ALL_MA(hist_weeks, self.todaystamp)              #上周周K线
            last0_max_week_ma = IndicatorUtils.ALL_MA(current_hist_weeks, TimeUtils.date_add(self.todaystamp, 7))              #本周周K
            last1_max_month_ma = IndicatorUtils.ALL_MA(hist_months, self.todaystamp)              #上月月K线
            last0_max_month_ma = IndicatorUtils.ALL_MA(current_hist_months, TimeUtils.lastday_of_month_from_datestamp(self.todaystamp))              #本月月K线



            last1_stock_week = current_hist_weeks[1] if len(current_hist_weeks) > 1 else None            #上周收盘周K线
            last0_stock_week = current_hist_weeks[0]    #本周收盘K线
            last1_stock_month = current_hist_months[1] if len(current_hist_months) > 1 else None                #上月收 盘月K线
            last0_stock_month = current_hist_months[0]   #本月收盘K线

	
            is_hit = True
	    is_hit_l_week = last1_stock_week is not None and last1_stock_week.close > 1.02 * last1_stock_week.op			   #上周收红
#	    is_hit_l_week = is_hit_l_week & (last1_stock_week.close > 0.99 * last1_max_week_ma)
#	    is_hit_l_week = is_hit_l_week & (realtime_stock_day.close > last0_max_week_ma)

	    is_hit_l_month = last1_stock_month is not None and last1_stock_month.close > 1.04 * last1_stock_month.op                          #上月收红
#           is_hit_l_month = is_hit_l_month & (last1_stock_month.close > 0.99 * last1_max_month_ma)
#           is_hit_l_month = is_hit_l_month & (realtime_stock_day.close > last0_max_month_ma)

	    is_hit = is_hit & (is_hit_l_week or is_hit_l_month)

	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)		#日均价上


            if is_hit:
		return ('CLWM-0', )

	except Exception, e:
	    traceback.print_exc()
	    LogUtils.info('exception data..' + jsonpickle.encode(realtime_stock_day))

	return None


