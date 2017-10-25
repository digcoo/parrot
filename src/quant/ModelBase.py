# encoding=utf-8

import time
import traceback
import jsonpickle as json

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

'''
'''
class ModelBase:

    def __init__(self, hist_days, hist_weeks, hist_months, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
	self.cache_hist_weeks = hist_weeks
	self.cache_hist_months = hist_months


    def match(self, realtime_stock_day):

	try:
	    hist_months = self.cache_hist_months[realtime_stock_day.symbol]
            hist_weeks = self.cache_hist_weeks[realtime_stock_day.symbol]
            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)

#	    last1_above_pressure_month_ma = IndicatorUtils.above_pressure_ma_tup(hist_months, self.todaystamp, realtime_stock_day.close)          #上月K线阻力位
            last0_above_pressure_month_ma = IndicatorUtils.above_pressure_ma_tup(hist_months, TimeUtils.date_add(TimeUtils.lastday_of_month_from_datestamp(self.todaystamp), 1), realtime_stock_day.close)
#           last1_above_pressure_week_ma = IndicatorUtils.above_pressure_ma_tup(hist_weeks, self.todaystamp, realtime_stock_day.close)        #上周K线阻力位
            last0_above_pressure_week_ma = IndicatorUtils.above_pressure_ma_tup(hist_weeks, TimeUtils.date_add(self.todaystamp, 7), realtime_stock_day.close)        #本周K线阻力位
#            last1_above_pressure_daily_ma = IndicatorUtils.above_pressure_ma_tup(hist_days, self.todaystamp, realtime_stock_day.close)          #昨日上方阻力位
            last0_above_pressure_daily_ma = IndicatorUtils.above_pressure_ma_tup(current_hist_days, TimeUtils.date_add(self.todaystamp, 7), realtime_stock_day.close)          #当天实时上方阻力位

            is_hit = True

	    #过滤本月月K线阻力位
	    is_last0_month_over_pressure = (last0_above_pressure_month_ma is None or realtime_stock_day.close < 0.95 * last0_above_pressure_month_ma[1])   #价格远离本月阻力至少5个点
	    is_hit = is_hit & (is_last0_month_over_pressure)
            #过滤本周周k线阻力位
            is_last0_week_over_pressure = (last0_above_pressure_week_ma is None or realtime_stock_day.close < 0.96 * last0_above_pressure_week_ma[1])   #当前价格远离本周阻力至少4个点
            is_hit = is_hit & (is_last0_week_over_pressure)
            #过滤当日日k线阻力位
#           LogUtils.info('symbol = ' + realtime_stock_day.symbol + ', daily pressure = ' + str(last1_above_pressure_daily_ma) + ', current close = ' + str(realtime_stock_day.close))
            is_last0_daily_over_pressure = (last0_above_pressure_daily_ma is None or realtime_stock_day.close < 0.97 * last0_above_pressure_daily_ma[1])  #价格远离上方阻力至少3个点
            is_hit = is_hit & (is_last0_daily_over_pressure)

#	    is_hit = is_hit & (realtime_stock_day.op > 0.985 * last1_stock_day.close)				#开盘幅度

	    is_hit = is_hit & (realtime_stock_day.close >= realtime_stock_day.op)				#收红

            is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * last1_stock_day.close)         #均价高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.994 * last1_stock_day.close)         #当前价格高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.996 * realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价

	    if is_hit:
		return ('BASE-0', )
	except Exception, e:
	    traceback.print_exc()

	return None


