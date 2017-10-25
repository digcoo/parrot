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
from IndicatorUtils import *

'''
开盘5分钟选股:前一天符合特殊K线，第二天又进一步惯性趋势
1、T型:
2、十字星
3、倒T型
4、上影线

'''
class ModelOpen:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days
        self.candidate_stocks = self.prepare_candidate_stocks()
#	print json.encode(self.candidate_stocks)
	self.candidate_stocks = CommonUtils.filter_symbol_dic(self.candidate_stocks)
#	print 'model_open candidate : ' + json.encode(self.candidate_stocks)

    def prepare_candidate_stocks(self):
	candidate_stocks = {}
	for symbol in self.cache_hist_days.keys():
            hist_days = self.cache_hist_days[symbol]
	    hit = self.match_candidate_model(hist_days)
	    if hit is not None:
		candidate_stocks[symbol] = hit
	return candidate_stocks

    # todo : 模型计算 
    def match_candidate_model(self, hist_days):
	try:
	    if hist_days is not None and len(hist_days) > 0:
		return self.Open(hist_days)
	except Exception, e:
	    traceback.print_exc()
	return None


    #昨日上影线 > 0.03  && 昨日红实体 && 红实体 < 0.04
    def Open(self, hist_days):
	last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
	last2_stock_day = BaseStockUtils.pre_stock_day(hist_days, 2, self.todaystamp)
	if last1_stock_day is None or last2_stock_day is None:
	    return None

	last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.todaystamp)
	last2_is_red = BaseStockUtils.pre_is_red(hist_days, 2, self.todaystamp)
	last1_upper_shadow = BaseStockUtils.pre_upper_shadow(hist_days, 1, self.todaystamp)
	last1_lower_shadow = BaseStockUtils.pre_lower_shadow(hist_days, 1, self.todaystamp)
	last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.todaystamp)
	last1_change_shadow = BaseStockUtils.pre_change_shadow(hist_days, 1, self.todaystamp)

	is_hit = True
	#上影线  or 下影线 or  十字星  or T型  
	#倒T:
	is_rt = True		
	is_rt = is_rt & (last1_is_red)		
        is_rt = is_rt & (last1_upper_shadow >= 0.02)      #昨日上影线
        is_rt = is_rt & (last1_column_shadow <= 0.04)       #昨日实体柱
        is_rt = is_rt & (last1_lower_shadow <= 0.006)     #昨日下影线
        is_rt = is_rt & (last1_upper_shadow > 2 * last1_column_shadow)

	#上吊线:防左侧压力线
        is_t = True
	is_t = is_t & (last1_is_red)	
        is_t = is_t & (last1_lower_shadow > 0.016)                      #下影线
        is_t = is_t & (last1_upper_shadow < 0.0065)                      #上影线
	is_t = is_t & (last1_change_shadow < 0.05)			#涨幅
        is_t = is_t & (last1_column_shadow > last1_upper_shadow)        #实体柱

	#十字星:
	is_star = True
	is_star = is_star & (last1_is_red)
        is_star = is_star & (last2_is_red)
        is_star = is_star & (last1_column_shadow <  min(last1_lower_shadow, last1_upper_shadow))      #上影线、下影线

        #昨日突破:
        is_last_break = True
	is_last_break = is_last_break & (last1_is_red or last1_change_shadow > 0)
        latest1_resistance_price_tup = BaseStockUtils.latest_resistance_price(hist_days, last1_stock_day) #昨日突破阻力位
        is_last_break = is_last_break & (latest1_resistance_price_tup is not None and last1_stock_day.close > 0.995 * latest1_resistance_price_tup[0])

#	if is_rt:
#            return ('OpenRT', )
	
	if is_t:
	    return ('OpenT', )

#        if is_star:
#            return ('OpenStar', )

	if is_last_break:
	    return ('OpenLastBreak', )	

	return None



    def match(self, realtime_stock_day):

        try:

#            当前时间段>9:30
#	    if TimeUtils.is_after('09:30:00'):
#		return None


            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None

            hist_days = self.cache_hist_days[realtime_stock_day.symbol]
            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.todaystamp)
            last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.todaystamp)
	    above_pressure_ma = IndicatorUtils.above_pressure_ma_tup(hist_days, self.todaystamp, realtime_stock_day.op)
	    last1_MAX_MA = IndicatorUtils.ALL_MA(hist_days, self.todaystamp)
	  
	    is_hit = True

	    is_hit = is_hit & (realtime_stock_day.op > 1.001 * last1_stock_day.close)         #高开
#	    if_hit = is_hit & (realtime_stock_day.op < 1.03 * last1_stock_day.close)		#高开幅度
#            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于收盘价
#            is_hit = is_hit & (realtime_stock_day.close > 1.003 *  last1_stock_day.close)         #当前价高于昨天收盘价
	    is_hit = is_hit & (above_pressure_ma is None or realtime_stock_day.close < 0.99 * above_pressure_ma[1])     #当前价偏离上方阻力位
#	    is_hit = is_hit & (BaseStockUtils.lower_shadow(realtime_stock_day) < 0.015)                         #下影线
	

	    is_hit = is_hit & (last1_MAX_MA is not None and last1_stock_day.close > 0.99 * last1_MAX_MA)           #昨日收盘价接近均线
	    is_hit = is_hit & (last1_MAX_MA is not None and realtime_stock_day.close > last1_MAX_MA)     #当前价高于昨日所有MA均线

            is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * last1_stock_day.close)         #均价高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.994 * last1_stock_day.close)         #当前价格高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.996* realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价


            if is_hit:
		return (self.candidate_stocks[realtime_stock_day.symbol][0], )

        except Exception, e:
            traceback.print_exc()

        return None




if __name__ == '__main__':
    geode_client = GeodeClient()
    symbol = 'sz002728'

    hist_symbols_days = {}
    latest_days = geode_client.query_stock_days_latest(symbol, 10)
    

    hist_symbols_days[symbol] = latest_days
    model_close = ModelOpen(hist_symbols_days, latest_days[0].day)
    today = latest_days[0]
    print model_close.match(today)

