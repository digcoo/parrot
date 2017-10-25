#encoding=utf-8
from utils.BaseStockUtils import *

import traceback
import jsonpickle


'''
潜伏涨幅超过5个点且处于调整状态
'''

class StockIncubator:

    def __init__(self, hist_days):
        self.cache_hist_days = hist_days
	self.stocks_weights = self.calc_weights(self.cache_hist_days)

    def calc_weights(self, cache_hist_days):
	stocks_weights = {}
	for symbol in cache_hist_days.keys():

	    #break_through
	    weight = self.calc_weight_for_break_through(cache_hist_days[symbol])
	    if weight is not None:
		stocks_weights[symbol] = weight
		continue


	    #continous_rise
#	    weight = self.calc_weight_for_continous_rise(cache_hist_days[symbol])
#            if weight is not None:
#                stocks_weights[symbol] = weight
	
	return stocks_weights


    def calc_weight_for_break_through(self, hist_days):			#最近10天
	try:
	    latest_hist_days = hist_days[0 :  min(8, len(hist_days))]
	    latest_hist_days.reverse()

	    break_stock_day = None
	    weight = -1
	    for stock_day in latest_hist_days:
		if self.break_through(stock_day):
		    break_stock_day = stock_day
		    weight = 0
		    continue
		
		if break_stock_day is not None and stock_day.close > stock_day.op and stock_day.close < break_stock_day.close:
		    weight = weight + 1

	    if break_stock_day is not None:
		return weight

	except Exception, e:
	    traceback.print_exc()
	return None


    def break_through(self, stock_day):
	return stock_day.last_close > 0 and (BaseStockUtils.change_shadow2(stock_day) > 0.05 or stock_day.high > 1.06 * stock_day.last_close)




    def calc_weight_for_continous_rise(self, hist_days):                 #最近20天
	if self.continous_rise(hist_days):
	    return 0
	return None



    def continous_rise(self, hist_days):
	try:
	    latest_hist_days = hist_days[0 :  min(20, len(hist_days))]
	    continous_rise_cnt = 0
	    continous_change_shadow = 0
	    for stock_day in latest_hist_days:
		if stock_day.close > stock_day.op:
		    continous_rise_cnt = continous_rise_cnt + 1
		    continous_change_shadow = continous_change_shadow + round((stock_day.close-stock_day.last_close)/stock_day.last_close, 5)
		    if continous_rise_cnt == 3 and continous_change_shadow > 0.04:
			return True
		else:
		    continous_rise_cnt = 0
		    continous_change_shadow = 0

	except Exception, e:
	    traceback.print_exc()

	return False
