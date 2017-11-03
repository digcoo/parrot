# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle


'''
1、日K线极度分散
'''
class ModelMAScatter:

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


            last1_ma5 = IndicatorUtils.MA(hist_days, 5, self.todaystamp)
            last1_ma10 = IndicatorUtils.MA(hist_days, 10, self.todaystamp)
            last1_ma20 = IndicatorUtils.MA(hist_days, 20, self.todaystamp)
            last1_ma30 = IndicatorUtils.MA(hist_days, 30, self.todaystamp)

	    over_mas = [last1_ma5, last1_ma10, last1_ma20, last1_ma30]
	    over_mas = list(filter(lambda x: x > realtime_stock_day, over_mas))		#上方阻力位

            is_hit = True
	    is_hit = is_hit & (BaseStockUtils.diverge_ma_hybridity(over_mas, 0.02))	#日ma线互相偏离
	    is_hit = is_hit & (realtime_stock_day.close > IndicatorUtils.Lowest_MA(hist_days, self.todaystamp))    		#昨日收盘价高于最低ma线
	    is_hit = is_hit & (realtime_stock_day.close < IndicatorUtils.ALL_MA(hist_days, self.todaystamp))			#昨日收盘价低于最高ma线
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)
	    is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > realtime_stock_day.last_close)

            if is_hit:
                return ('MAScatter-0', )

	except Exception, e:
	    traceback.print_exc()

	return None



