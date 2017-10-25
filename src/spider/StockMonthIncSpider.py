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

class StockMonthIncSpider:

    def __init__(self):
	self.geode_client = GeodeClient.get_instance()

    def get_allstocks_month(self):
	#本月底
	lastday_of_current_month = TimeUtils.lastday_of_month_from_datestamp(TimeUtils.get_current_datestamp())
	LogUtils.info('stock_month_inc_spider start, current_last_day_of_month = ' + TimeUtils.timestamp2datestring(lastday_of_current_month) + '\n')
	stocks_month = []
	symbols = self.geode_client.query_all_stock_symbols()
	fail_symbols = []
	for symbol in symbols:
#            if symbol != 'sh603055':
#        	continue

#	    LogUtils.info('===============================stock_month_inc symbol[%s] start============================================\n' % (symbol, ))
	    try:
		stock_days = self.geode_client.query_stock_days_latest(symbol, 32)
		com_stock_days_tup = self.compose_hist_days_from_current_month(symbol, stock_days)
#		LogUtils.info('current month stock_days : ' + jsonpickle.encode(com_stock_days_tup[0]) + '\n')
		if com_stock_days_tup is not None and com_stock_days_tup[0] is not None and len(com_stock_days_tup[0]) > 0:
		    stock_month = self.caculate_stock_month_data(symbol, com_stock_days_tup[0], com_stock_days_tup[1], lastday_of_current_month)
		    stocks_month.append(stock_month)
#		    LogUtils.info('current_stock_month: ' + jsonpickle.encode(stock_month) + '\n')
		else:
		    fail_symbols.append(symbol)
	    except Exception, e:
		traceback.print_exc()
		fail_symbols.append(symbol)
#	    LogUtils.info('===============================stock_month_inc symbol[%s] end============================================\n\n' % (symbol, ))

#	    break
	
	if len(stocks_month) > 0:
	    self.geode_client.add_batch_stock_months(stocks_month)

	print 'current month no stock_month : ' + jsonpickle.encode(fail_symbols) + ', and failed num = ' + str(len(fail_symbols))


    #本月的日交易记录
    def compose_hist_days_from_current_month(self, symbol, hist_days):
	if hist_days is None or len(hist_days) == 0:
	    return None
	hist_days.reverse()
#	print jsonpickle.encode(hist_days)
	current_datestamp = TimeUtils.get_current_datestamp()
	current_month_days = []
	last_month_stock_day = None
	for stock_day in hist_days:
	    if TimeUtils.is_same_month_with_datestamp(current_datestamp, stock_day.day):
		current_month_days.append(stock_day)
	    else:
		last_month_stock_day = stock_day
	return (current_month_days, last_month_stock_day)

    #计算一月的数据
    def caculate_stock_month_data(self, symbol, stock_month_days, last_stock_month, month_lastday_datestamp):
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
        stock_month.day = last_stock_day.day
	stock_month.last_close = last_stock_month.close if last_stock_month is not None else None
        stock_month.id = symbol + TimeUtils.timestamp2datestring(month_lastday_datestamp).replace('-', '')
        return stock_month


if __name__ == '__main__':
    month_inc_spider = StockMonthIncSpider()
    month_inc_spider.get_allstocks_month()

