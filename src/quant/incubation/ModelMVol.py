# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle


'''
收盘5分钟选股：当前符合特殊K线
1、近几日调整:
2、今日大幅缩量收红
'''
class ModelMVol:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
	self.candidate_stocks = self.prepare_candidate_stocks()

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
                return self.MVol(hist_days)
        except Exception, e:
            traceback.print_exc()
        return None


    #昨日缩量
    def MVol(self, hist_days):
	last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
	last2_stock_day = BaseStockUtils.pre_stock_day(hist_days, 2, self.todaystamp)
	last3_stock_day = BaseStockUtils.pre_stock_day(hist_days, 3, self.todaystamp)
	last4_stock_day = BaseStockUtils.pre_stock_day(hist_days, 4, self.todaystamp)
	last5_stock_day = BaseStockUtils.pre_stock_day(hist_days, 5, self.todaystamp)
#	last6_stock_day = BaseStockUtils.pre_stock_day(hist_days, 6, self.todaystamp)
	if last1_stock_day is None or last2_stock_day is None or last3_stock_day is None or last4_stock_day is None or last5_stock_day is None:
	    return None

	min5_vol = min(last2_stock_day.vol, last3_stock_day.vol, last4_stock_day.vol, last5_stock_day.vol)

	is_m_vol = True
	is_m_vol = is_m_vol & (last1_stock_day.vol < min5_vol)

        if is_m_vol:
            return ('MVol', )
        return None


    def match(self, realtime_stock_day):
        try:

            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None
	
            hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)

	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)

	    if last1_stock_day is None:
		return None

            is_hit = True
#	    is_hit = is_hit & (BaseStockUtils.lower_shadow(realtime_stock_day) < 0.015)                         #下影线

            if is_hit:
		return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-0', )

	except Exception, e:
	    traceback.print_exc()
	return None

