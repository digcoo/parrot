#encoding=utf-8
import os
from sys import path
path.append(os.getcwd() + '/backtest')
path.append(os.getcwd() + '/quant')
path.append(os.getcwd() + '/vo')
path.append(os.getcwd() + '/utils')
path.append(os.getcwd() + '/utils/incubation')
path.append(os.getcwd() + '/dbs')

import jsonpickle as json

from GeodeClient import *
from RedisClient import *
from SinaStockUtils import *
from ParseForSinaUtils import *
from ThsStockUtils import *
from IndicatorUtils import *

from CloseTest import *
from ModelSunrise import *
from ModelVol import *
from ModelMinV import *
from ModelT import *
from ModelRT import *
from ModelStar import *
from ModelGreenT import *
from ModelOpen import *
from ModelCloseT import *
from ModelBurst import *
from ModelMAScatter import *
from ModelCloseSRedHead import *
from ModelCloseBRedHead import *
from StockIncubator import *
from ModelLastBreak import *
from ModelUpper import *
from ModelCrossDMA import *
from ModelMVol import *
from ModelBase import *
from ModelNDWMA import *
from ModelReMarket import *
from ModelDNWMA import *
from ModelMonthMA import *
from ModelWatch import *
from ModelTimeMA import *
from ModelTime30 import *
from ModelLastTime30 import *
from ModelTimeRise import *
from ModelCover import *
from ModelTimeMin import *
from ModelTimeV60 import *
from ModelBoard import *


from analyzer.StockTimeAnalyzer import *
from spider.StockTimeIncSpider import *
from spider.StockTimeIncForSinaSpider import *

class BackTest:

    def __init__(self):
	self.geode_client = GeodeClient()
	self.redis_client = RedisClient()
	self.symbols = self.geode_client.query_all_stock_symbols()
	self.test_days = 1

    def import_stocks_days(self):
	symbols = self.geode_client.query_all_stock_symbols()
	finish_cnt = 0
	for symbol in symbols:
	    finish_cnt += 1
	    if finish_cnt < 1400:
		continue
	    stock_days = self.geode_client.query_stock_days_latest(symbol, 10000);
	    for i in range(len(stock_days) - 1):
		stock_days[i].last_close = stock_days[i+1].close
#	    print json.encode(stock_days)
#	    break
	    self.geode_client.add_batch_stock_days(stock_days)
	    
	    print symbol + ':' + str(finish_cnt)



    def latest_resistance_price(self, symbol):

	try:

            hist_symbols_days = {}
 
            latest_days = self.geode_client.query_stock_days_latest(symbol, 1000)

#            stock_today = SinaStockUtils.get_sina_stock_day(symbol)[0]

	    stock_today = latest_days[1]	    
	    print TimeUtils.timestamp2datestring(stock_today.day)

            latest_resistance = BaseStockUtils.latest_resistance_price(latest_days, stock_today)

            if latest_resistance is not None and len(latest_resistance) > 0:
		print latest_resistance[0]
                return latest_resistance[0]

	except Exception, e:
	    print e
	    traceback.print_exc()
	return None

    def test_hit(self):
	cnt = 0
	for symbol in self.symbols:
	    hist_days = self.geode_client.query_stock_days_latest(symbol, 300)
	    self.test_for_close(hist_days, symbol)
	    cnt += 1
	    if cnt >= 2000:
		break

    def test_for_close(self, hist_days, symbol):
	test_close = CloseTest(hist_days, symbol, self.test_days)
	test_close.test()


    def test_for_symbol_incubator(self, symbol):

        geode_client = GeodeClient()

        hist_symbols_days = {}

        latest_days = geode_client.query_stock_days_latest(symbol, 30)

        stock_today = SinaStockUtils.get_sina_stock_day(symbol)[0]

        hist_symbols_days[symbol] = latest_days

        model_test = StockIncubator(hist_symbols_days)


    def test_for_indicator(self, symbol):

        geode_client = GeodeClient()

        latest_days = geode_client.query_stock_days_latest(symbol, 30)

	print IndicatorUtils.MA(latest_days, 5, 0)

    def test_for_history_recommend(self):
	target_intv = 2
	todaystamp = TimeUtils.get_current_datestamp()
	stock_analyzer = StockAnalyzer(time_cache=None, with_gem=False, todaystamp=todaystamp)
        symbols = self.geode_client.query_all_stock_symbols()
	symbols = CommonUtils.filter_symbols(symbols)
	hit_list = []
	loop = 0
        for symbol in symbols:
	    try:
#		if symbol != 'sh600619':
#		    continue
		loop = loop + 1
		LogUtils.info('loop=' + str(loop) + ', symbol=' + symbol)
		if loop > 100:
		    break
		hist_days = stock_analyzer.latest_days[symbol]
	  	LogUtils.info('stub_day = ' + TimeUtils.timestamp2datestring(hist_days[target_intv].day))	
		stock_analyzer = StockAnalyzer(time_cache=None, with_gem=False, todaystamp=hist_days[target_intv].day)
        	hit = stock_analyzer.match(hist_days[target_intv])
       		if hit is not None:
           	    hit_list.append(hit)
	    except Exception, e:
		print 'no data exception, symbol = ' + symbol
		traceback.print_exc()
#	self.redis_client.put_all_today(hit_list)
	print json.encode(hit_list)	




    def test_for_symbol_today_match(self, symbol):

        geode_client = GeodeClient()

        hist_symbols_days = {}

        latest_days = geode_client.query_stock_days_latest(symbol, 300)

#       stock_today = SinaStockUtils.get_sina_stock_day(symbol)[0]

        stock_today = latest_days[0]

#       print json.encode(stock_today)

        hist_symbols_days[symbol] = latest_days

        model_test = ModelMAScatter(hist_symbols_days, stock_today.day)

        print model_test.match(stock_today)




    def test_for_week_ma_match(self, symbol):

        geode_client = GeodeClient()

        hist_symbols_days = {}
        hist_symbols_weeks = {}

        latest_days = geode_client.query_stock_days_latest(symbol, 300)
        latest_weeks = geode_client.query_stock_weeks_latest(symbol, 300)

#       stock_today = SinaStockUtils.get_sina_stock_day(symbol)[0]

        stock_today = latest_days[0]
	print 'stub_stock_day = ' + stock_today.id

#       print json.encode(stock_today)

        hist_symbols_days[symbol] = latest_days
        hist_symbols_weeks[symbol] = latest_weeks
#       print json.encode(latest_weeks[0:50])

        model_test = ModelBase(hist_symbols_days, hist_symbols_weeks, stock_today.day)

        print model_test.match(stock_today)




    def test_for_month_ma_match(self, symbol):

        geode_client = GeodeClient.get_instance()

        hist_symbols_days = {}
        hist_symbols_weeks = {}
	hist_symbols_months = {}

        latest_days = geode_client.query_stock_days_latest(symbol, 300)
        latest_weeks = geode_client.query_stock_weeks_latest(symbol, 300)
	latest_months = geode_client.query_stock_months_latest(symbol, 300)

#       stock_today = SinaStockUtils.get_sina_stock_day(symbol)[0]

        stock_today = latest_days[0]
        print 'stub_stock_day = ' + stock_today.id

#       print json.encode(stock_today)

        hist_symbols_days[symbol] = latest_days
        hist_symbols_weeks[symbol] = latest_weeks
	hist_symbols_months[symbol] = latest_months
#       print json.encode(latest_weeks[0:50])

        model_test = ModelBase(hist_symbols_days, hist_symbols_weeks, hist_symbols_months, stock_today.day)

        print model_test.match(stock_today)

    def test_for_time_ma_match(self, symbol):
	hist_symbols_days = {}

	latest_days = GeodeClient.get_instance().query_stock_days_latest(symbol, 300)
	latest_times = GeodeClient.get_instance().query_stock_time_trades_map_by_idlist([symbol])

	hist_symbols_days[symbol] = latest_days

	latest_times = ParseForSinaUtils.compose_stock_times_from_daytimes_map(latest_times)
#	print jsonpickle.encode(latest_times[symbol][0])

#	print jsonpickle.encode(latest_times)

	today_stamp = TimeUtils.get_current_datestamp()
	model_test = ModelTimeV60(hist_symbols_days, latest_times, today_stamp)

	today_stamp, today_times, last_close = ThsStockUtils.get_realtime_time_stock_trades(symbol)
	
#	print jsonpickle.encode(today_times)
	realtime_stock_day = BaseStockUtils.compose_realtime_stock_day_from_time_trades(today_times, symbol=symbol, last_close=last_close, today_stamp=today_stamp)

	print model_test.match(realtime_stock_day, today_times)

    def test_for_spider(self, symbol):
#	symbols = GeodeClient.get_instance().query_all_stock_symbols()

#	symbols = CommonUtils.filter_symbols(symbols)

#	symbols = list(filter(lambda x: x == 'sz002117', symbols))

	symbols = [symbol]

	stock_analyzer = StockTimeAnalyzer(symbols, TimeUtils.get_current_datestamp())

	spider = StockTimeIncForSinaSpider(stock_analyzer = stock_analyzer, symbols = symbols, inc_persist = False, hit_persist = False, identify='time-0-0')

	spider.get_all_stocks_realtime_trades()
	



    def test_for_board_today_match(self, symbol):

        geode_client = GeodeClient()

        hist_symbols_days = {}

        latest_days = geode_client.query_stock_days_latest(symbol, 300)

#       stock_today = SinaStockUtils.get_sina_stock_day(symbol)[0]

        stock_today = latest_days[0]

        model_test = ModelBoard(stock_today.day)

        print model_test.match(stock_today)



if __name__ == '__main__':
    base_test = BackTest()
#    base_test.test_hit()
#    base_test.test_for_symbol_today_match('sh601086')
#    base_test.test_for_week_ma_match('sz000058')
#    base_test.test_for_month_ma_match('sz000633')
#    base_test.test_for_time_ma_match('sz002227')
    base_test.test_for_spider('sh603323')
#    base_test.test_for_board_today_match('sh603533')

#    base_test.import_stocks_days()
#    base_test.latest_resistance_price('sz000008')
#    base_test.latest_resistance_price('sz002842')

#    base_test.test_for_symbol_incubator('sh603757')

#    base_test.test_for_indicator('sz002729')

#    base_test.test_for_history_recommend()
