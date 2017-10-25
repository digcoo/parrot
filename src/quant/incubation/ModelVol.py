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
1、昨日大阳收盘:
2、今日大幅缩量调整
'''
class ModelVol:

    def __init__(self, hist_days, today):
	self.today = today
        self.cache_hist_days = hist_days

    def validate(self, hist_days):
	if len(hist_days) < 2:
	    return False
	return True

	

    def match(self, realtime_stock_day):
        try:
	
#            当前时间段>2:30
            if not TimeUtils.is_after('14:40:00'):
                return None

            hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)

            if not self.validate(hist_days):
                return None

            is_hit = True
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.today)
            last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.today)

            last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.today)

            is_hit = is_hit & (last1_is_red and last1_column_shadow > 0.03)						#昨日涨幅
	    is_hit = is_hit & (realtime_stock_day.vol < 0.5 * last1_stock_day.vol)			#昨日量比
		
            is_hit = is_hit & (realtime_stock_day.close > 0.995 * realtime_stock_day.op)                #当前价高于收盘价
	    is_hit = is_hit & (BaseStockUtils.change_shadow(realtime_stock_day, last1_stock_day) < 0.04)
#            is_hit = is_hit & (realtime_stock_day.close > last1_stock_day.close)         #当前价高于昨天收盘价
#            is_hit = is_hit & (realtime_stock_day.close > (realtime_stock_day.money/realtime_stock_day.vol))         #当前价高于均价
            is_hit = is_hit & (CommonUtils.filter_stock(realtime_stock_day) is not None)		#过滤创业板

            if is_hit:
		return BaseStockUtils.compose_hit_data(realtime_stock_day, 'Vol')

	except Exception, e:
	    traceback.print_exc()
	return None



if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sz300546'
    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 1000)
    day_index = 96

    print json.encode(latest_days[day_index])

    hist_symbols_days[symbol] = latest_days
    model_close = ModelVol(hist_symbols_days, latest_days[day_index].day)
    today = latest_days[day_index]
    print model_close.match(today)
