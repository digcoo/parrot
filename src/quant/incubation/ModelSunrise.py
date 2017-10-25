# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/vo')
import time
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from CommonUtils import *
'''
1、底部三连升
'''
class ModelSunrise:

    def __init__(self, hist_days, today):
	self.today = today
        self.cache_hist_days = hist_days      
        self.candidate_stocks = self.prepare_candidate_stocks()
#	print 'model_sunrise candidate : ' + json.encode(self.candidate_stocks)

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
		return self.Sunrise(hist_days)
	except Exception, e:
	    print e
	return None


    #连续3日上升
    def Sunrise(self, hist_days):
	last1_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 1, self.today)
	last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.today)
	last2_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 2, self.today)
	last2_is_red = BaseStockUtils.pre_is_red(hist_days, 2, self.today)
	last3_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 3, self.today)
	last3_is_red = BaseStockUtils.pre_is_red(hist_days, 3, self.today)
        last4_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 4, self.today)
        last4_is_red = BaseStockUtils.pre_is_red(hist_days, 4, self.today)
        last5_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 5, self.today)
        last5_is_red = BaseStockUtils.pre_is_red(hist_days, 5, self.today)
        last2_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 2, self.today)
        last3_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 3, self.today)
        last4_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 4, self.today)
        last5_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 5, self.today)


#	last3_r_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 3, self.today)	#连续三日的复利涨幅
	#最近连续三日飘红
	latest1_is_sunrise = True
	latest1_is_sunrise = latest1_is_sunrise & (last1_change_shadow > 0 and last1_is_red)
	latest1_is_sunrise = latest1_is_sunrise & (last2_change_shadow > 0 and last2_is_red)
	latest1_is_sunrise = latest1_is_sunrise & (last3_change_shadow > 0 and last3_is_red)
#	latest1_is_sunrise = latest1_is_sunrise & (last1_change_shadow + last2_change_shadow + last3_change_shadow > 0.03)

	#昨日连续3日飘红+收绿
        latest2_is_sunrise = True
        latest2_is_sunrise = latest2_is_sunrise & (last2_column_shadow > 0 and last2_is_red)
        latest2_is_sunrise = latest2_is_sunrise & (last3_column_shadow > 0 and last3_is_red)
        latest2_is_sunrise = latest2_is_sunrise & (last4_column_shadow > 0 and last4_is_red)
        latest2_is_sunrise = latest2_is_sunrise & (last1_change_shadow < 0 and not last1_is_red)
#        latest2_is_sunrise = latest2_is_sunrise & (last2_column_shadow + last3_column_shadow + last4_column_shadow > 0.02)
	

        #前日连续3日飘红+收绿
        latest3_is_sunrise = True
        latest3_is_sunrise = latest3_is_sunrise & (last3_column_shadow > 0 and last3_is_red)
        latest3_is_sunrise = latest3_is_sunrise & (last4_column_shadow > 0 and last4_is_red)
        latest3_is_sunrise = latest3_is_sunrise & (last5_column_shadow > 0 and last5_is_red)
        latest3_is_sunrise = latest3_is_sunrise & (last1_change_shadow < 0 and not last1_is_red)
        latest3_is_sunrise = latest3_is_sunrise & (last2_change_shadow < 0 and not last2_is_red)
#        latest3_is_sunrise = latest3_is_sunrise & (last3_column_shadow + last4_column_shadow + last5_column_shadow > 0.02)

	if latest1_is_sunrise:
            return ('Sunrise-0', )

        if latest2_is_sunrise:
            return ('Sunrise-1', )

        if latest3_is_sunrise:
            return ('Sunrise-2', )
	
	return None


    def match(self, realtime_stock_day):
	try:
	
	    if realtime_stock_day.symbol not in self.candidate_stocks.keys():
		return None

	    hist_days = self.cache_hist_days[realtime_stock_day.symbol]
	    last_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.today)
	    
	    is_hit = True
#           is_hit = is_hit & (realtime_stock_day.op > last_stock_day.op)
#           is_hit = is_hit & (realtime_stock_day.op > last_stock_day.close)         #高开 
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于收盘价
            is_hit = is_hit & (realtime_stock_day.close > last_stock_day.close)         #当前价高于昨天收盘价
            is_hit = is_hit & (realtime_stock_day.close > round(realtime_stock_day.money/realtime_stock_day.vol, 5))         #当前价高于均价

            if is_hit:
		return (self.candidate_stocks[realtime_stock_day.symbol][0], )

	except Exception, e:
	    traceback.print_exc()

	return None

