# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/vo')
import time
import traceback
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from TimeUtils import *
from CommonUtils import *
from WeightUtils import *
from IndicatorUtils import *

class ModelWatch:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days

    def match(self, realtime_stock_day):
        try:
	
            hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)
	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
	    if last1_stock_day is None:
		return None

            is_hit = True
	    is_hit = is_hit & (BaseStockUtils.change_shadow2(realtime_stock_day) > 0.018 and BaseStockUtils.change_shadow2(realtime_stock_day) < 0.054)

            if is_hit:
                return ('Watch-0', )

	except Exception, e:
	    traceback.print_exc()
	return None


