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

'''
收盘5分钟选股：当前符合特殊K线
1、倒T型小阳线:
2、T型小实体
3、小头实体
'''
class ModelCloseT:

    def __init__(self, hist_days, today):
	self.today = today
        self.cache_hist_days = hist_days

    def validate(self, hist_days):
	if len(hist_days) < 4:
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
	    last2_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 2, self.today)
		
            upper_shadow = round(abs(realtime_stock_day.high - realtime_stock_day.close)/realtime_stock_day.close, 5)
            lower_shadow = round(abs(realtime_stock_day.low - realtime_stock_day.op)/realtime_stock_day.op, 5)
            column_shadow = round(abs(realtime_stock_day.close - realtime_stock_day.op)/realtime_stock_day.op, 5)

            is_red = (realtime_stock_day.close > realtime_stock_day.op)

            #吊脚线
            is_t = True
            is_t = is_t & (last2_is_red & (last2_change_shadow < 0.05))				#前天收红
            is_t = is_t & (last1_stock_day.close > 0.998 * last1_stock_day.op)		#昨天收红或小阴
            is_t = is_t & (last1_upper_shadow > 2 * last1_column_shadow)			#昨天倒T,留下上影线
	    is_t = is_t & ((last1_lower_shadow < 0.01) & (last1_lower_shadow < last1_upper_shadow))	#昨天，较小下影线
		
            is_t = is_t & (realtime_stock_day.op < 1.0086 * last1_stock_day.close)		#回避高开
	    is_t = is_t & (lower_shadow > 0.018)			#下影线
	    is_t = is_t & (column_shadow > 0.006)			#实体柱
	    is_t = is_t & ((upper_shadow < 2 * column_shadow) & (upper_shadow < 0.035))		#回避上影线

            is_hit = is_hit & (is_t)	
		
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于收盘价
#            is_hit = is_hit & (realtime_stock_day.close > last1_stock_day.close)         #当前价高于昨天收盘价
            is_hit = is_hit & (realtime_stock_day.close > (realtime_stock_day.money/realtime_stock_day.vol))         #当前价高于均价
#            is_hit = is_hit & (CommonUtils.filter_stock(realtime_stock_day) is not None)		#过滤创业板
    
#	    print 'today = ' + TimeUtils.timestamp2datestring(self.today) + '-' + str(is_hit)
  
            if is_hit:
		return BaseStockUtils.compose_hit_data(realtime_stock_day, 'CloseT')

	except Exception, e:
	    traceback.print_exc()

	return None


if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sh600111'
    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 100)
    hist_symbols_days[symbol] = latest_days
    model_close = ModelCloseT(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)
