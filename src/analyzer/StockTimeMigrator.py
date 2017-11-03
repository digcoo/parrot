#coding=utf-8

import traceback
import jsonpickle
import time
from dto.DataContainer import *
from analyzer.StockTimeAnalyzer import *
from spider.StockTimeIncSpider import *
from spider.StockTimeIncForEMSpider import *
from spider.StockTimeIncForSinaSpider import *
from utils.LogUtils import *

class StockTimeMigrator:

    stock_time_inc_spider = None

    def __init__(self, symbols, todaystamp, identify):
	
	LogUtils.info('==============stock_time_migrator_init, identify = ({0}) start========================================'.format(identify))
	
	start  = int(time.mktime(datetime.datetime.now().timetuple()))

	self.identify = identify
	self.stock_time_analyzer = None
	try:
	    self.stock_time_analyzer = StockTimeAnalyzer(symbols = symbols, todaystamp=todaystamp)
	    market_symbols = self.stock_time_analyzer.data_container.market_symbols
	    print'StockTimeMigrator market_symbols = ' +  str(len(market_symbols))
	    self.stock_time_inc_spider = StockTimeIncForSinaSpider(stock_analyzer=self.stock_time_analyzer, symbols = market_symbols, inc_persist=False, hit_persist=True, identify = self.identify)
	except Exception, e:
	    traceback.print_exc()

        end = int(time.mktime(datetime.datetime.now().timetuple()))
        LogUtils.info('stock_time_migrator_init take %s seconds' % (str(end - start), ))
        LogUtils.info('==============stock_time_migrator_init, identify = ({0}) end========================================\n\n'.format(identify))


    def start(self):
	try:

	    self.stock_time_inc_spider.get_all_stocks_realtime_trades()

	except Exception, e:
	    traceback.print_exc()



if __name__ == '__main__':
    symbols = GeodeClient.get_instance().query_all_stock_symbols()

    symbols = CommonUtils.filter_symbols(symbols)

    symbols = list(filter(lambda x: x == 'sh600330', symbols))

    time_migrator = StockTimeMigrator(symbols = symbols, todaystamp = TimeUtils.get_current_datestamp(), identify='time-0')

    time_migrator.start()

