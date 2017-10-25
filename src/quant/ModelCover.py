# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle as json


'''
1、反包策略
'''
class ModelCover:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days      

    def match(self, realtime_stock_day):

	try:

            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

	    current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)


            is_hit = True

	    is_hit = is_hit & (last1_stock_day.close < 0.99 * last1_stock_day.op)		#昨日收阴绿体
            is_hit = is_hit & (realtime_stock_day.close > last1_stock_day.op)                #完成反包
            is_hit = is_hit & (realtime_stock_day.close > round(realtime_stock_day.money/realtime_stock_day.vol, 5))         #当前价高于均价

#            is_hit = is_hit & (realtime_stock_day.close > max(last1_stock_day.close, last1_stock_day.op))         #当前价格高于昨日收盘价
#	    is_hit = is_hit & (realtime_stock_day.close > last0_ma5)						#当前价格高于当前MA5

            if is_hit:
                return ('Cover-0', )

	except Exception, e:
	    traceback.print_exc()

	return None



