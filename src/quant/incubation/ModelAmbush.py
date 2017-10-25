# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/vo')
import time
import traceback
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from CommonUtils import *

'''
1、潜伏选股:曾经大涨过
'''
class ModelAmbush:

    def __init__(self, hist_days, today):
	self.today = today
	self.cache_hist_days = hist_days

    def match(self, realtime_stock_day):

	try:

            stock_hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(stock_hist_days, 1, self.today)

            if last1_stock_day is None:
                return None

	    last1_is_red = BaseStockUtils.pre_is_red(stock_hist_days, 1, self.today)

	    is_hit = True

            is_hit = is_hit & (last1_is_red)                                                #昨日收红
            is_hit = is_hit & (realtime_stock_day.op > last1_stock_day.close)                  #高开
            is_hit = is_hit & (realtime_stock_day.low < max(realtime_stock_day.op, last1_stock_day.close))                  #下降调整
            is_hit = is_hit & (realtime_stock_day.low > 0.985 * min(realtime_stock_day.op, last1_stock_day.close))          #小幅调整

            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)             #当前价高于开盘价
            is_hit = is_hit & (realtime_stock_day.close > 1.004 * last1_stock_day.close)              #当前价高于昨天收盘价,且偏离0轴
            is_hit = is_hit & (realtime_stock_day.close > (realtime_stock_day.money/realtime_stock_day.vol))         #当前价高于均价
	    is_hit = is_hit & (BaseStockUtils.change_shadow2(realtime_stock_day) < 0.055)

	    if is_hit:
		return ('Ambush-0',)


	except Exception, e:

	    traceback.print_exc()

	return None

if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sz002728'

    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 10)


    hist_symbols_days[symbol] = latest_days
    model_close = ModelMinV(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)

