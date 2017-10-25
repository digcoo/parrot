# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')
import time
import traceback
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from CommonUtils import *
'''
1、十字星模型:Star
'''
class ModelStar:

    def __init__(self, hist_days, today):
	self.today = today
        self.cache_hist_days = hist_days      
        self.candidate_stocks = self.prepare_candidate_stocks()
#	print 'model_star candidate : ' + json.encode(self.candidate_stocks)

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
		return self.Star(hist_days)
	except Exception, e:
	    print e
	return None


    #昨日上影线 > 0.03  && 昨日红实体 && 红实体 < 0.04
    def Star(self, hist_days):
	last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.today)
        last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.today)		#实体柱
	last1_upper_shadow = BaseStockUtils.pre_upper_shadow(hist_days, 1, self.today)
	last1_lower_shadow = BaseStockUtils.pre_lower_shadow(hist_days, 1, self.today)
	is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.today)				#昨日收红

	is_candidate = True
#	is_candidate = is_candidate & is_red
#	is_candidate = is_candidate & (last1_column_shadow <= 0.03)			#昨日实体柱
#	is_candidate = is_candidate & (last1_upper_shadow >= 0.0085)			#上影线
#	is_candidate = is_candidate & (last1_lower_shadow >= 0.0085)			#下影线

	is_candidate = is_candidate & (last1_stock_day.close > 0.998 * last1_stock_day.op)
	is_candidate = is_candidate & (last1_column_shadow <  min(last1_lower_shadow, last1_upper_shadow))	#上影线、下影线

	if is_candidate:
            return ('Star', )
	return None

    def match(self, realtime_stock_day):


        try:

            candinate_stock = None

            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None

	    hist_days = self.cache_hist_days[realtime_stock_day.symbol]
	    last_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.today)
	    if last_stock_day is None:
		return None

	    is_hit = True
	    
	    is_hit = is_hit & (realtime_stock_day.op > 0.99 * last_stock_day.close)         #高开
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)		#当前价高于开盘价
	    is_hit = is_hit & (realtime_stock_day.close > 1.004 * last_stock_day.close)		#当前价高于昨天收盘价
	    is_hit = is_hit & (realtime_stock_day.close > (realtime_stock_day.money/realtime_stock_day.vol))         #当前价高于均价
#	    is_hit = is_hit & (BaseStockUtils.change_shadow2(realtime_stock_day) < 0.055)		#涨幅
	    is_hit = is_hit & (abs(BaseStockUtils.lower_shadow(realtime_stock_day)) < 0.015)             #下影线

            if is_hit:
		return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-0', )

        except Exception, e:
            traceback.print_exc()

        return None



if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sz002728'

    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 10)


    hist_symbols_days[symbol] = latest_days
    model_close = ModelStar(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)

