# encoding=utf8 
from sys import path
#path.append('/home/ubuntu/scripts/gemfire')
path.append('/home/ubuntu/scripts/vo')
path.append('/home/ubuntu/scripts/utils')
#from GemfireClient import *
from gemfire import *
import time
import datetime
import traceback
from StockDayInfo import *
import jsonpickle
from GeodeClient import *
from TimeUtils import *

'''

'''

class StockWeekImport:

    def __init__(self):
	self.geode_client = GeodeClient()

    def import_all(self):
	loop = 0
	symbols = self.geode_client.query_all_stock_symbols()
	fail_symbols = []
	for symbol in symbols:
	    try:
		loop += 1
#		if loop < 1470:
#		    continue
#		if symbol != 'sz002427':
#		    continue
		stock_days = self.geode_client.query_stock_days_latest(symbol, 10000)	
		com_stock_days = self.compose_hist_days_from_2010(symbol, stock_days)
#		print 'com_stock_days = ' + jsonpickle.encode(com_stock_days)
		stock_weeks = self.compose_stock_weeks(symbol, com_stock_days)
#		print 'stock_weeks = ' + jsonpickle.encode(stock_weeks)
		stock_weeks = self.compose_final_stock_weeks(stock_weeks)
		print 'stock week import ing, symbol = ' + symbol + ', loop = ' + str(loop) + ', week_size = ' + str(len(stock_weeks)) + '\n\n'
#		print 'stock_weeks:' + jsonpickle.encode(stock_weeks) + '\n\n'
		self.geode_client.add_batch_stock_weeks(stock_weeks)
	    except Exception, e:
		traceback.print_exc()
		fail_symbols.append(symbol)
		print 'except, symbol = ' + symbol + '\n\n'
	print 'fail_symbols = ' + jsonpickle.encode(fail_symbols) + '\n\n'

    #将hist_days封装为按时间轴顺序的stock_days,以空间换时间
    def compose_hist_days_from_2010(self, symbol, hist_days):
	if hist_days is None or len(hist_days) == 0:
	    return None
	hist_days.reverse()
	new_hist_days = []
	start_stamp = hist_days[0].day
	
	#截至到本周五数据，如果不到本周，则填充
	current_weekday = TimeUtils.day_of_week_from_datestamp(hist_days[len(hist_days)-1])
        current_friday = TimeUtils.date_add(TimeUtils.get_current_datestamp(), 5 - current_weekday)
#        end_stamp = hist_days[len(hist_days)-1].day
	end_stamp = current_friday
	day_cnt = (end_stamp - start_stamp) / (24 * 60 * 60) + 1

	day_index = 0

	for loop in range(0, day_cnt):
	    cur_stamp = TimeUtils.date_add(start_stamp, loop)
	    is_exist = False
	    for i in range(day_index, len(hist_days)):
		if hist_days[i].day == cur_stamp:
		    is_exist = True
		    day_index = i
		    new_hist_days.append(hist_days[i])

	    if not is_exist:
		vir_stock_day = StockDayInfo()
		vir_stock_day.day = cur_stamp
		vir_stock_day.id = symbol + TimeUtils.timestamp2datestring(cur_stamp).replace('-', '')
		new_hist_days.append(vir_stock_day)

	return new_hist_days

    #封装轴线数据
    def compose_stock_weeks(self, symbol, hist_days):
	stock_weeks = []
	stock_week_days = []
	for i in range(0, len(hist_days)):
	    stock_day = hist_days[i]
	    date_obj = datetime.datetime.fromtimestamp(stock_day.day)
	    if date_obj.isoweekday() in range(1, 5 + 1):
		stock_week_days.append(stock_day)
		if date_obj.isoweekday() == 5:       #周五
		    stock_week = self.caculate_stock_week_data(stock_week_days, symbol, stock_day.day)
		    if stock_week is not None and stock_week.vol > 0:
			stock_weeks.append(stock_week)
		    del stock_week_days[0:len(stock_week_days)]

		elif i == len(hist_days) - 1:
                    stock_week = self.caculate_stock_week_data(stock_week_days, symbol, stock_day.day)
                    if stock_week is not None and stock_week.vol > 0:
                        stock_weeks.append(stock_week)
		    del stock_week_days[0:len(stock_week_days)]

	return stock_weeks


    #计算一周的数据
    def caculate_stock_week_data(self, stock_week_days, symbol, weekday_stamp):
	if stock_week_days is None or len(stock_week_days) == 0:
	    return None

	week_high = 0.1
        week_low = 999999
	week_close = 0
	week_op = 0
	week_vol = 0
	week_money = 0
	last_stock_day = None

	for stock_day in stock_week_days:
	    if stock_day.close is not None and stock_day.close > 0.1:
		week_high = week_high if week_high > stock_day.high else stock_day.high
		week_low = week_low if week_low < stock_day.low else stock_day.low
		week_vol = week_vol + stock_day.vol
		week_money = week_money + stock_day.money
		if week_op == 0:
		    week_op = stock_day.op
		last_stock_day = stock_day

	if week_close < 0.1 and last_stock_day is not None:
	    week_close = last_stock_day.close

	stock_week = StockDayInfo()
	stock_week.op = week_op
	stock_week.close = week_close
	stock_week.high = week_high
 	stock_week.low = week_low
	stock_week.vol = week_vol
	stock_week.money = week_money
	stock_week.symbol = symbol
	stock_week.day = weekday_stamp
	stock_week.id = symbol + TimeUtils.timestamp2datestring(weekday_stamp).replace('-', '')
	return stock_week

    def compose_final_stock_weeks(self, stock_weeks):
	if stock_weeks is not None and len(stock_weeks) > 1:
	    for i in range(1, len(stock_weeks)):
		stock_weeks[i].last_close = stock_weeks[i-1].close
	return stock_weeks

week_import = StockWeekImport()
week_import.import_all()
