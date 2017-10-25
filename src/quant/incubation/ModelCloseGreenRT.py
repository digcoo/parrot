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
收盘5分钟选股：当前符合特殊K线
1、倒T型小阳线:
2、T型小实体
3、小头实体
'''
class ModelCloseGreenRT:

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

            last2_is_red = BaseStockUtils.pre_is_red(hist_days, 2, self.today)
		
            upper_shadow = round(abs(realtime_stock_day.high - realtime_stock_day.close)/realtime_stock_day.close, 5)
            lower_shadow = round(abs(realtime_stock_day.low - realtime_stock_day.op)/realtime_stock_day.op, 5)
            column_shadow = round(abs(realtime_stock_day.close - realtime_stock_day.op)/realtime_stock_day.op, 5)

            is_red = (realtime_stock_day.close > realtime_stock_day.op)

            #大阴后阳柱
            is_green_rt = True
            is_green_rt = is_green_rt & (not last1_is_red)					#收绿
            is_green_rt = is_green_rt & (last1_column_shadow > 0.015 or last1_change_shadow > 0.02)  #绿体柱 或 跌幅超过2%
            is_green_rt = is_green_rt & ((column_shadow > 0.0086) & (upper_shadow < 0.5 * column_shadow))	#小阳柱：回避上影线,谨防左侧压力位

            is_hit = is_hit & (is_green_rt)
		
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于收盘价
#            is_hit = is_hit & (realtime_stock_day.close > last1_stock_day.close)         #当前价高于昨天收盘价
            is_hit = is_hit & (realtime_stock_day.close > (realtime_stock_day.money/realtime_stock_day.vol))         #当前价高于均价
#            is_hit = is_hit & (CommonUtils.filter_stock(realtime_stock_day) is not None)		#过滤创业板
    
#	    print 'today = ' + TimeUtils.timestamp2datestring(self.today) + '-' + str(is_hit)
 
            if is_hit:
		return BaseStockUtils.compose_hit_data(realtime_stock_day, 'CloseGreenRT')


	except Exception, e:
	    traceback.print_exc()
	return None



if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sh600111'
    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 100)
    hist_symbols_days[symbol] = latest_days
    model_close = ModelCloseGreenRT(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)
