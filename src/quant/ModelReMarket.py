# encoding=utf-8

from utils.BaseStockUtils import *
from utils.IndicatorUtils import *
from dto.DataContainer import *

import time
import traceback
import jsonpickle


'''
1、停盘后复盘
'''
class ModelReMarket:

    def __init__(self, hist_days, data_container, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
	self.data_container = data_container
        self.candidate_stocks = self.prepare_candidate_stocks()
	LogUtils.info('ModelReMarket candinates : ' + json.encode(self.candidate_stocks))

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
		return self.ReMarket(hist_days)
	except Exception, e:
	    traceback.print_exc()
	return None


    #昨日停盘票
    def ReMarket(self, hist_days):

	is_re_market = True
	is_re_market = is_re_market & (hist_days[0].symbol in self.data_container.re_market_symbols)

	if is_re_market:
            return ('ReMark', )
	return None


    def match(self, realtime_stock_day):

	try:

            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None

	    is_hit = True
		
#	    is_hit = is_hit & (realtime_stock_day.close > 0.998 * realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均线
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价

            if is_hit:
                return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-' +  str(0), )

	except Exception, e:
	    traceback.print_exc()

	return None



