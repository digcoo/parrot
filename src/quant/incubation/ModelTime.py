# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/vo')

import time
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *

'''
昨日K线：十字星、T型小阳线、倒T阳线、较长上影线、大阴实体

1、均线稳定上升、价格线稳定上升,价格线不能过分偏离均线
2、上冲均线（有蓄势）
'''
class ModelTime:

    def __init__(self, time_cache):
        self.time_cache = time_cache

    def filter(self, candidate_symbol):
	if(symbol[0 : 3] != 'sz3'):
	    return candidate_symbol
	return None

    def Time(self, stock_time_cache):
	if stock_time_cache is not None:
	    close_cache,avg_cache = self.compose(stock_time_cache)
	    is_hit = False
	    is_hit = is_hit | self.upper_avg(close_cache, avg_cache)		#是否稳定运行在均线之上
	    is_hit = is_hit | self.cross_avg(high_cache, low_cache, close_cache, avg_cache)	#
	    is_hit = is_hit | self.cross_high(high_cache, close_cache, avg_cache)	#是否突破新高
	    return is_hit
	return False

    def compose(self, stock_time_cache):
	high_cache = []
	low_cache = []
	close_cache = []
	avg_cache = []
	
	for i in range(1, len(stock_time_cache)):
	    high_cache.append(stock_time_cache[i][0])
	    low_cache.append(stock_time_cache[i][1])
	    close_cache.append(stock_time_cache[i][2])
	    avg_cache.append(stock_time_cache[i][3])
	return (high_cache, low_cache, close_cache, avg_cache)
	
    

    #80%时间段价格运行在均线之上
    def upper_avg(self, close_cache, avg_cache):
	total = 0
	target_cnt = 0
	for i in range(0, len(close_cache)):
	    total += 1
	    if close_cache[i] >= avg_cache[i]:
		target_cnt += 1		
	return target_cnt / total > 0.6

    #上冲均线，并且稳定运行在均线之上，且有突破前高动能(2种情况：一直在开盘线之上、且涨幅在>3%,突破前高；在开盘价附近：缓缓上升突破最好)
    def cross_avg(self, high_cache, low_cache, close_cache, avg_cache):
	is_upper_cross = False
	is_low_cross = False
	is_surpass_high = False			#调整之后是否有突破前高
	for i in range(0, len(close_cache)):
	    high = high_cache[i]
	    low = high_cache[i]
	    close = high_cache[i]
	    avg = avg_cache[i]
	    if(round((high-avg)/avg, 5) > 0.005):
		is_upper_cross = True
	    
	    if (round((avg-low)/low, 5) > 0.005):
		is_low_cross = True
	return is_upper_cross & is_low_cross

    #突破前高 (间隔频率:5min):最近5分钟有突破
    def cross_high(self, high_cache, close_cache, avg_cache):
	is_surpass_high = False                 #调整之后是否有突破前高
	interval = 5
	tmp_high = -1
	if len(close_cache) < interval * 6 + 1:
	    return is_surpass_high
        for i in range(len(close_cache) - interval * 6, len(close_cache)):
            high = high_cache[i]
            low = high_cache[i]
            close = high_cache[i]
            avg = avg_cache[i]
	    if i % interval == 0:
		if tmp_high < 0:
		    tmp_high = high
		else:
		    is_surpass_high = high > tmp_high
		    break
	return is_surpass_high

    def match(self, realtime_stock_day):
	is_hit = True
	
        is_hit = is_hit & (realtime_stock_day.close > round(realtime_stock_day.money/realtime_stock_day.vol, 5))	#均线之上
	if not is_hit:
	    return False
	is_hit = is_hit & (self.Time(self.time_cache.get(realtime_stock.day.symbol)))
	return is_hit

if __name__ == '__main__':
    model_time = ModelTime({})
