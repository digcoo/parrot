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
from GeodeClient import *

'''
1、实阴线 + 高开收稳

'''
class ModelGreenT:

    def __init__(self, hist_days, today):
	self.today = today
        self.cache_hist_days = hist_days      


    def match(self, realtime_stock_day):

	try:

	    hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)
	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.today)
	    last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.today)            #实体柱	
	    last1_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 1, self.today)
	    last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.today)

	    is_hit = True
	    is_hit = is_hit & (CommonUtils.filter_stock(realtime_stock_day) is not None)
	    is_hit = is_hit & (not last1_is_red) & (last1_column_shadow > 0.015 or last1_change_shadow > 0.018)             #昨日大阴
	    is_hit = is_hit & (realtime_stock_day.op > 0.994 * last1_stock_day.close)         #高开
	    is_hit = is_hit & (realtime_stock_day.low > 0.99 * min(last1_stock_day.op, last1_stock_day.close))         #倒T
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于收盘价
	    is_hit = is_hit & (realtime_stock_day.close > 1.004 * last1_stock_day.close)         #当前价高于昨天收盘价
	    is_hit = is_hit & (realtime_stock_day.close > round(realtime_stock_day.money/realtime_stock_day.vol, 5))         #当前价高于均价


            if is_hit:
		return BaseStockUtils.compose_hit_data(realtime_stock_day, 'GreenT')


	except Exception, e:
	    traceback.print_exc()

	return None


if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sz002728'

    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 10)


    hist_symbols_days[symbol] = latest_days
    model_close = ModelGreenT(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)

