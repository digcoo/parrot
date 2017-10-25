# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')

import time
import traceback
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from TimeUtils import *
from CommonUtils import *


'''
尾盘小双头大阳线：
1、回避抄底反弹股
2、寻找左侧有支撑位
'''
class ModelCloseSRedHead:

    def __init__(self, hist_days, today):
	self.today = today
        self.cache_hist_days = hist_days

    def validate(self, hist_days):
	if len(hist_days) < 3:
	    return False
	return True

	

    def match(self, realtime_stock_day):
        try:
	
#            当前时间段>2:30
#            if TimeUtils.compare_current('14:40:00') > 0 :
#                return False

            hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)

            if not self.validate(hist_days):
                return False

	
            is_hit = True
           
	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.today)
            last1_upper_shadow = BaseStockUtils.pre_upper_shadow(hist_days, 1, self.today)
            last1_lower_shadow = BaseStockUtils.pre_lower_shadow(hist_days, 1, self.today)
            last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.today)
            last1_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 1, self.today)
            last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.today)

	    last2_stock_day = BaseStockUtils.pre_stock_day(hist_days, 2, self.today)
            last2_is_red = BaseStockUtils.pre_is_red(hist_days, 2, self.today)
		
            upper_shadow = round(abs(realtime_stock_day.high - realtime_stock_day.close)/realtime_stock_day.close, 5)
            lower_shadow = round(abs(realtime_stock_day.low - realtime_stock_day.op)/realtime_stock_day.op, 5)
            column_shadow = round(abs(realtime_stock_day.close - realtime_stock_day.op)/realtime_stock_day.op, 5)

            is_red = (realtime_stock_day.close > last1_stock_day.close)

            #小双头大阳线:双头线越短越适宜
            is_sdouble_red_head = True
#	    latest_red_stock_day = BaseStockUtils.latest_red_day(hist_days, 1, self.today)
#	    is_sdouble_red_head = is_sdouble_red_head & (realtime_stock_day.close > 0.997 * latest_red_stock_day.close)
	    is_sdouble_red_head = is_sdouble_red_head & (not last1_is_red)			#昨日收绿
            is_sdouble_red_head = is_sdouble_red_head & (is_red)				#收红
            is_sdouble_red_head = is_sdouble_red_head & (column_shadow > 0.01)			#实体柱
            is_sdouble_red_head = is_sdouble_red_head & (column_shadow > max(upper_shadow, lower_shadow)) #双头线

            is_hit = is_hit & (is_sdouble_red_head)	
		
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于收盘价
#            is_hit = is_hit & (realtime_stock_day.close > last1_stock_day.close)         #当前价高于昨天收盘价
            is_hit = is_hit & (realtime_stock_day.close > (realtime_stock_day.money/realtime_stock_day.vol))         #当前价高于均价
#            is_hit = is_hit & (CommonUtils.filter_stock(realtime_stock_day) is not None)		#过滤创业板
    
#	    print 'today = ' + TimeUtils.timestamp2datestring(self.today) + '-' + str(is_hit)

            if is_hit:
		return BaseStockUtils.compose_hit_data(realtime_stock_day, 'CloseSRedHead')


	except Exception, e:
	    traceback.print_exc()
	return None



if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sh600288'
    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 200)
    hist_symbols_days[symbol] = latest_days
    for index in range(len(latest_days)):
	cursor_stock_day = latest_days[index]
        model_close = ModelCloseSRedHead(hist_symbols_days, cursor_stock_day.day)
    	print TimeUtils.timestamp2datestring(cursor_stock_day.day) + str( model_close.match(cursor_stock_day))
