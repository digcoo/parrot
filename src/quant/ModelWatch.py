# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *

import time
import traceback
import jsonpickle

'''
1、当日早盘分时下降调整，后V型反转(昨日收红、今日微服高开最佳)
2、当日光头阳线(昨日收绿最佳)
'''
class ModelWatch:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
	self.cache_hist_days = hist_days

    def match(self, realtime_stock_day):

	try:
	    is_hit = realtime_stock_day.close > 1.045 * realtime_stock_day.last_close

	    if is_hit:
		return ('Watch-0',)


	except Exception, e:
	    traceback.print_exc()

	return None
