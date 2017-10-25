# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle


'''
1、上影线
'''
class ModelUpper:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days      
        self.candidate_stocks = self.prepare_candidate_stocks()
#	print 'model_upper candidate : ' + json.encode(self.candidate_stocks)

    def prepare_candidate_stocks(self):
	candidate_stocks = {}
	for symbol in self.cache_hist_days.keys():
            hist_days = self.cache_hist_days[symbol]
	    hit = self.match_candidate_model(hist_days)
	    if hit is not None:
		candidate_stocks[symbol] = hit
	return candidate_stocks

    # todo : 模型计算 
    def match_candidate_model(self, hist_days):
	try:
	    if hist_days is not None and len(hist_days) > 0:
		return self.Upper(hist_days)
	except Exception, e:
	    traceback.print_exc()
	return None


    #上影线
    def Upper(self, hist_days):
	last1_upper_shadow = BaseStockUtils.pre_upper_shadow(hist_days, 1, self.todaystamp)		#上影线
	last1_lower_shadow = BaseStockUtils.pre_lower_shadow(hist_days, 1, self.todaystamp)		#下影线
        last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.todaystamp)		#实体柱
	last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.todaystamp)				#昨日收红

	is_upper = True
	is_upper = is_upper & (last1_is_red)
	is_upper = is_upper & (last1_upper_shadow >= 0.02)	#昨日上影线
#	is_upper = is_upper & (last1_column_shadow <= 0.04)	#昨日实体柱
	is_upper = is_upper & (last1_lower_shadow < 0.015)	#昨日下影线

	is_upper = is_upper & (last1_upper_shadow > last1_column_shadow and last1_upper_shadow > last1_lower_shadow)

	if is_upper:
            return ('Upper', )
	return None


    def match(self, realtime_stock_day):

	try:

            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None

            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)

            last1_max_daily_ma = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)              #昨日日K线
            last0_max_daily_ma = IndicatorUtils.ALL_MA(current_hist_days, TimeUtils.date_add(self.todaystamp, 7))              #今日日K线
	    last0_ma5	       = IndicatorUtils.MA(current_hist_days, 5, self.todaystamp) 

            is_hit = True

            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于开盘价
            is_hit = is_hit & (realtime_stock_day.close > round(realtime_stock_day.money/realtime_stock_day.vol, 5))         #当前价高于均价

#	    is_hit = is_hit & (BaseStockUtils.lower_shadow(realtime_stock_day) < 0.015)                         #下影线

#            is_hit = is_hit & (last1_max_daily_ma is not None and last1_stock_day.close > 0.99 * last1_max_daily_ma)           #昨日收盘价接近昨日日K线均线
#            is_hit = is_hit & (last0_max_daily_ma is not None and realtime_stock_day.close > last0_max_daily_ma)           #当前价高于当日日K均线

            is_hit = is_hit & (realtime_stock_day.close > max(last1_stock_day.close, last1_stock_day.op))         #当前价格高于昨日收盘价
#	    is_hit = is_hit & (realtime_stock_day.close > last0_ma5)						#当前价格高于当前MA5

            if is_hit:
                return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-' +  str(0), )

	except Exception, e:
	    traceback.print_exc()

	return None



