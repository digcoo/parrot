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

class StockMonthImport:

    def __init__(self):
	self.geode_client = GeodeClient.get_instance()

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
#		print 'com_stock_days_size = ' + str(len(com_stock_days))
		stock_months = self.compose_stock_months(symbol, com_stock_days)
#		print 'stock_months = ' + jsonpickle.encode(stock_months)
#		print 'stock_months_size = ' + str(len(stock_months))
		stock_months = self.compose_final_stock_months(stock_months)
		print 'stock month import ing, symbol = ' + symbol + ', loop = ' + str(loop) + ', month_size = ' + str(len(stock_months)) + '\n\n'
#		print 'stock_months:' + jsonpickle.encode(stock_months) + '\n\n'
		self.geode_client.add_batch_stock_months(stock_months)
	    except Exception, e:
		traceback.print_exc()
		fail_symbols.append(symbol)
		print 'except, symbol = ' + symbol + '\n\n'

#	    break
	print 'fail_symbols = ' + jsonpickle.encode(fail_symbols) + '\n\n'

    #将hist_days封装为按时间轴顺序的stock_days,以空间换时间
    def compose_hist_days_from_2010(self, symbol, hist_days):
	if hist_days is None or len(hist_days) == 0:
	    return None
	hist_days.reverse()
	new_hist_days = []
	start_stamp = hist_days[0].day
	
	#截至到本周五数据，如果不到本周，则填充
	current_year = TimeUtils.year_from_datestamp(hist_days[len(hist_days)-1].day)
	current_month = TimeUtils.month_from_datestamp(hist_days[len(hist_days)-1].day)
        current_month_last_day = TimeUtils.lastday_of_month(current_year, current_month)
	end_stamp = current_month_last_day
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
    def compose_stock_months(self, symbol, hist_days):
	stock_months = []
	stock_month_days = []
	is_new_month = False
	for i in range(0, len(hist_days)):
	    stock_day = hist_days[i]
	    stock_month_days.append(stock_day)
	    if not is_new_month:
		is_new_month = True

	    if TimeUtils.is_lastday_of_month_from_datestamp(stock_day.day):	#本月的最后一天
		stock_month = self.caculate_stock_month_data(stock_month_days, symbol, stock_day.day)
		if stock_month is not None and stock_month.vol > 0:
		    stock_months.append(stock_month)
		    del stock_month_days[0:len(stock_month_days)]
		is_new_month = False

	    elif i == len(hist_days) - 1:
		stock_month = self.caculate_stock_month_data(stock_month_days, symbol, stock_day.day)
		if stock_month is not None and stock_month.vol > 0:
		    stock_months.append(stock_month)
		    del stock_month_days[0:len(stock_month_days)]
		
	return stock_months


    #计算一月的数据
    def caculate_stock_month_data(self, stock_month_days, symbol, month_lastday_stamp):
	if stock_month_days is None or len(stock_month_days) == 0:
	    return None

	month_high = 0.1
        month_low = 999999
	month_close = 0
	month_op = 0
	month_vol = 0
	month_money = 0
	last_stock_day = None

	for stock_day in stock_month_days:
	    if stock_day.close is not None and stock_day.close > 0.1:
		month_high = month_high if month_high > stock_day.high else stock_day.high
		month_low = month_low if month_low < stock_day.low else stock_day.low
		month_vol = month_vol + stock_day.vol
		month_money = month_money + stock_day.money
		if month_op == 0:
		    month_op = stock_day.op
		last_stock_day = stock_day

	if month_close < 0.1 and last_stock_day is not None:
	    month_close = last_stock_day.close

	stock_month = StockDayInfo()
	stock_month.op = month_op
	stock_month.close = month_close
	stock_month.high = month_high
 	stock_month.low = month_low
	stock_month.vol = month_vol
	stock_month.money = month_money
	stock_month.symbol = symbol
	stock_month.day = month_lastday_stamp
	stock_month.id = symbol + TimeUtils.timestamp2datestring(month_lastday_stamp).replace('-', '')
	return stock_month

    def compose_final_stock_months(self, stock_months):
	if stock_months is not None and len(stock_months) > 1:
	    for i in range(1, len(stock_months)):
		stock_months[i].last_close = stock_months[i-1].close
	return stock_months

month_import = StockMonthImport()
month_import.import_all()
