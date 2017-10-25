# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback

from utils.ObjectUtils import *
from utils.HttpUtils import *
from utils.ParseForThsUtils import *
from dbs.MysqlClient import *
from dbs.GeodeClient import *
from vo.PlateInfo import *
from vo.PlateDayInfo import *
'''
同花顺实时交易
'''
class StockTimeIncForThsSpider:

    def __init__(self):
        self.stock_timely_realtime_url = 'http://d.10jqka.com.cn/v6/time/hs_{0}/today.js'		#code
        self.stock_daily_realtime_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/01/today.js'             #code
        self.stock_weekly_realtime_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/11/today.js'             #code
        self.stock_monthly_realtime_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/21/today.js'   #code
        self.stock_detail_url = 'http://stockpage.10jqka.com.cn/{0}/'                   #code(stock.id[2:])


    def get_all_stocks_realtime_trades(self):
	symbols = GeodeClient.get_instance().query_all_stock_symbols()
	fail_symbols = []
        for symbol in symbols:
	    try:
		LogUtils.info('=================================stock_time_inc_for_ths, symbol=%s======================================================\n' % (symbol, ))
		date_stamp, realtime_time_stock_trades = self.get_realtime_time_stock_trades(symbol)
		if realtime_time_stock_trades is not None:
		    GeodeClient.get_instance().put_stock_time_trades(symbol, date_stamp, realtime_time_stock_trades)

		    LogUtils.info('get_realtime_time_stock_trades, symbol = ' + symbol + ', trades_size = ' + str(len(realtime_time_stock_trades))+ '\n')
		else:
		    fail_symbols.append(symbol)
	    except Exception, e:
		traceback.print_exc()
		fail_symbols.append(symbol)
	LogUtils.info('stock_time_inc_for_ths, fail_symbols_size = ' + str(len(fail_symbols)) + ', fail_symbols = ' + jsonpickle.encode(fail_symbols) + '\n')

    def get_realtime_time_stock_trades(self, symbol):
	stock = StockInfo()
	stock.id = symbol
        url = self.stock_timely_realtime_url.format(stock.id[2:])
        content = self.get_html(url, stock)
        date_stamp, stock_realtime_time_trades, last_close = ParseForThsUtils.parse_realtime_time_stock_trades(content, stock)
	return date_stamp, stock_realtime_time_trades
	

    def get_html(self, url, stock):
        try:
	    headers = {}
	    headers['Referer'] = self.stock_detail_url.format(stock.id[2:])
            ntries = 100
	    loop = 0
            while loop < ntries:
		loop += 1
                content = HttpUtils.get(url, headers, 'gbk')
                if content is not None:
                    return content

                LogUtils.info('html get content exception, now retry %s times' % (loop, ))

                time.sleep(5)              #wait5s
        except Exception, e:
            traceback.print_exc()

        return None

if __name__ == '__main__':
    spider = StockTimeIncForThsSpider()
    spider.get_all_stocks_realtime_trades()

