# encoding=utf8 
import time
import datetime
import traceback
from vo.StockDayInfo import *
import jsonpickle
from dbs.GeodeClient import *
from utils.TimeUtils import *
from utils.LogUtils import *
'''

'''

class StockWeekIncSpider:

    def __init__(self):
	self.geode_client = GeodeClient.get_instance()

    def get_allstocks_week(self):
	#本周五日期
	current_weekday = TimeUtils.day_of_week_from_datestamp(TimeUtils.get_current_datestamp())
	LogUtils.info('stock_week_inc_spider start, current_weekday = ' + str(current_weekday) + '\n')
	current_friday = TimeUtils.date_add(TimeUtils.get_current_datestamp(), 5 - current_weekday)
#	LogUtils.info('current_friday = ' + TimeUtils.timestamp2datestring(current_friday) + '\n')
	stocks_week = []
	symbols = self.geode_client.query_all_stock_symbols()
	fail_symbols = []
	loop = 0
	for symbol in symbols:
	    loop += 1
#	    if symbol != 'sh603136':
#		continue 
#	    LogUtils.info('=====================stock_week_inc symbol[%s] start============================================\n' % (symbol, ))
	    try:
		stock_days = self.geode_client.query_stock_days_latest(symbol, 8)
		com_stock_days_tup = self.compose_hist_days_from_current_week(symbol, stock_days)
#		LogUtils.info('current week stock_days : ' + jsonpickle.encode(com_stock_days_tup[0]) + '\n')
		if com_stock_days_tup is not None and com_stock_days_tup[0] is not None and len(com_stock_days_tup[0]) > 0:
		    stock_week = self.caculate_stock_week_data(symbol, com_stock_days_tup[0], com_stock_days_tup[1], current_friday)
		    stocks_week.append(stock_week)
#		    LogUtils.info('current_stock_week: ' + jsonpickle.encode(stock_week) + '\n')
		else:
		    fail_symbols.append(symbol)
	    except Exception, e:
		traceback.print_exc()
		fail_symbols.append(symbol)
#	    break
#	    LogUtils.info('=====================stock_week_inc symbol[%s], size = %s end============================================\n\n' % (symbol,loop ))

#	LogUtils.info('save stock_weeks = ' + jsonpickle.encode(stocks_week))

	if len(stocks_week) > 0:
	    self.geode_client.add_batch_stock_weeks(stocks_week)

	LogUtils.info('current week no stock_week : ' + jsonpickle.encode(fail_symbols) + ', and failed num = ' + str(len(fail_symbols)))


    #本周的日交易记录
    def compose_hist_days_from_current_week(self, symbol, hist_days):
	if hist_days is None or len(hist_days) == 0:
	    return None
	hist_days.reverse()
#	print jsonpickle.encode(hist_days)
	current_datestamp = TimeUtils.get_current_datestamp()
	today_week_days = []
	last_week_stock_day = None
	for stock_day in hist_days:
	    tmp_w = TimeUtils.week_of_month_from_datestamp(stock_day.day)
	    if TimeUtils.is_same_week_with_datestamp(stock_day.day, current_datestamp):
		today_week_days.append(stock_day)
	    else:
		last_week_stock_day = stock_day
	return (today_week_days, last_week_stock_day)

    #计算一周的数据
    def caculate_stock_week_data(self, symbol, stock_week_days, last_week_stock_day, current_friday_datestamp):
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
	    if stock_day.close is not None:
		week_high = week_high if week_high > stock_day.high else stock_day.high
		week_low = week_low if week_low < stock_day.low else stock_day.low
		week_vol = week_vol + stock_day.vol
		week_money = week_money + stock_day.money
		if week_op == 0:
		    week_op = stock_day.op
		last_stock_day = stock_day
	if week_close == 0:
	    week_close= last_stock_day.close

	stock_week = StockDayInfo()
	stock_week.op = week_op
	stock_week.close = week_close
	stock_week.high = week_high
 	stock_week.low = week_low
	stock_week.vol = week_vol
	stock_week.money = week_money
	stock_week.symbol = symbol
	stock_week.day = last_stock_day.day
	stock_week.last_close = last_week_stock_day.close if last_week_stock_day is not None else None
	stock_week.id = symbol + TimeUtils.timestamp2datestring(current_friday_datestamp).replace('-', '')
	return stock_week

    def compose_final_stock_weeks(self, stock_weeks):
	if stock_weeks is not None and len(stock_weeks) > 1:
	    for i in range(1, len(stock_weeks)):
		stock_weeks[i].last_close = stock_weeks[i-1].close
	return stock_weeks

if __name__ == '__main__':
    week_inc_spider = StockWeekIncSpider()
    week_inc_spider.get_allstocks_week()

