#encoding=utf-8

from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/quant/incubation')

from CommonUtils import *
from TimeUtils import *
from FileUtils import *
from ModelTime30 import *


class TimeTest:

    #一支票的历史记录
    def __init__(self, hist_days, hist_times_map, symbol, test_days):
	self.hist_times_map = hist_times_map
	self.hist_days = hist_days
	self.symbol = symbol
	self.test_days = test_days

    def test(self):
	if self.hist_times_map is not None:
	    return self.test_for_time30()				#尾盘30分收红

    #尾盘30分钟收红实体
    def test_for_time30(self):
	hit_indexs = []
	days = self.hist_times_map.keys()
	days = sorted(days)
#	print 'days : ' + jsonpickle.encode(days)
	for day in days:

	    cur_stock_times = self.hist_times_map.get(day)

	    index, realtime_stock_day = self.get_stock_day(day)

#	    print jsonpickle.encode(realtime_stock_day)

            model_time30 = ModelTime30({self.symbol:self.hist_days}, None, int(str(day)))

#	    last_close = local_stock_day.close
#	    realtime_stock_day = BaseStockUtils.compose_realtime_stock_day_from_time_trades(cur_stock_times, symbol=self.symbol, last_close=last_close, today_stamp=day)
	   
	    cur_day = TimeUtils.timestamp2datestring(int(str(day))) 
            if model_time30.match(realtime_stock_day, cur_stock_times):
#		print self.symbol + '- hit - ' + cur_day

                hit_indexs.append(index)
#	    else:
#		print self.symbol + '- not hit - ' + cur_day
	    
	print self.symbol + ' hit indexs = ' + jsonpickle.encode(hit_indexs)
#        FileUtils.output_backup_test(self.symbol, 'ModelTime30', self.hist_days, hit_indexs, self.test_days)
	lines_data = FileUtils.compose_lines_data(self.symbol, self.hist_days, hit_indexs, self.test_days)
	return 'ModelTime30', lines_data

    def get_stock_day(self, day):
	for i in range(len(self.hist_days)):
	    if self.hist_days[i].day == int(str(day)):
		return i, self.hist_days[i]
	return None, None


