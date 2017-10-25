# encoding=utf-8

import time
import traceback
import jsonpickle

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *


'''
1、反弹突破阻力位

'''
class ModelBurst:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days      
#        self.candidate_stocks = self.prepare_candidate_stocks()
#	print 'model_burst candidate : ' + jsonpickle.encode(self.candidate_stocks)

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
		return self.Burst(hist_days)
	except Exception, e:
	    traceback.print_exc()
	return None


    #昨日上影线 > 0.03  && 昨日红实体 && 红实体 < 0.04
    def Burst(self, hist_days):
	try:
            last4_rebound_day = BaseStockUtils.pre_rebound_day(hist_days, 4)
            last3_rebound_day = BaseStockUtils.pre_rebound_day(hist_days, 3)
            last2_rebound_day = BaseStockUtils.pre_rebound_day(hist_days, 2)
            last1_rebound_day = BaseStockUtils.pre_rebound_day(hist_days, 1)

            is_candidate = True
            is_candidate = is_candidate & (last3_rebound_day.close/last2_rebound_day.close < 1.00 * last2_rebound_day.close/last1_rebound_day.close)        #斜率

            if is_candidate:
                return ('Burst', )

	except Exception, e:
	    traceback.print_exc()	
	return None


    def match(self, realtime_stock_day):
	try:
            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)

            last1_max_daily_ma = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)              #昨日日K线
            last0_max_daily_ma = IndicatorUtils.ALL_MA(current_hist_days, TimeUtils.date_add(self.todaystamp, 7))              #今日日K线

	    latest_resistance_price_tup = BaseStockUtils.latest_resistance_price(hist_days, realtime_stock_day)	#突破阻力位

	    is_hit = True

	    is_hit = is_hit & (latest_resistance_price_tup is not None and realtime_stock_day.close > 1.003 * latest_resistance_price_tup[0])
	    #realtime_stock_day.close < 1.6 * latest_resistance_price_tup[0])
	    
	
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)		#当前价高于开盘价
#	    is_hit = is_hit & (realtime_stock_day.close > 1.004 * last1_stock_day.close)		#当前价高于昨天收盘价
#	    is_hit = is_hit & (BaseStockUtils.lower_shadow(realtime_stock_day) < 0.015)				#下影线

            is_hit = is_hit & (last1_max_daily_ma is not None and last1_stock_day.close > 0.99 * last1_max_daily_ma)           #昨日收盘价接近昨日日K线均线
	    is_hit = is_hit & (last0_max_daily_ma is not None and realtime_stock_day.close > last0_max_daily_ma)           #当前价高于当日日K均线
	
	    is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * last1_stock_day.close)		#均价高于昨日收盘价
	    is_hit = is_hit & (realtime_stock_day.close > 0.994 * last1_stock_day.close)         #当前价格高于昨日收盘价
	    is_hit = is_hit & (realtime_stock_day.close > 0.996 * realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价

            if is_hit:
		return ('Burst-' + str(0), )

	except Exception, e:
	    traceback.print_exc()

	return None


