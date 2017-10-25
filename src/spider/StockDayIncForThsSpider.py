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
class StockDayIncForThsSpider:

    def __init__(self):
        self.stock_timely_realtime_url = 'http://d.10jqka.com.cn/v6/time/hs_{0}/today.js'		#code
        self.stock_daily_realtime_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/01/today.js'             #code
        self.stock_weekly_realtime_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/11/today.js'             #code
        self.stock_monthly_realtime_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/21/today.js'   #code
        self.stock_detail_url = 'http://stockpage.10jqka.com.cn/{0}/'                   #code(stock.id[2:])


    def get_all_stocks_realtime_trades(self):
        all_stocks = GeodeClient.get_instance().query_all_stocks()
        all_stocks = ObjectUtils.dic_2_object(all_stocks)

        for stock in all_stocks:
	    try:
		#realtime_min
		realtime_time_stock_trades, last_close = self.get_realtime_time_stock_trades(stock)
		LogUtils.info('get_realtime_time_stock_trades, symbol = ' + stock.id + ', trades_size = ' + str(len(realtime_time_stock_trades))+ '\n')

		#realtime_day
		realtime_day_stock_trades = self.get_realtime_day_stock_trades(stock)
		realtime_day_stock_trades.last_close = last_close
		LogUtils.info('get_realtime_day_stock_trades, symbol = ' + stock.id + ', trades = ' + jsonpickle.encode(realtime_day_stock_trades) + '\n')
		

		#realtime_week
		realtime_week_stock_trades = self.get_realtime_week_stock_trades(stock)
		LogUtils.info('get_realtime_week_stock_trades, symbol = ' + stock.id + ', trades = ' + jsonpickle.encode(realtime_week_stock_trades) + '\n')
		

		#realtime_month
		realtime_month_stock_trades = self.get_realtime_month_stock_trades(stock)
		LogUtils.info('get_realtime_month_stock_trades, symbol = ' + stock.id + ', trades = ' + jsonpickle.encode(realtime_month_stock_trades) + '\n')
		

		LogUtils.info('=================================stock_day_inc_for_ths, symbol=%s======================================================\n' % (stock.id, ))
	    except Exception, e:
		traceback.print_exc()

    def get_realtime_time_stock_trades(self, stock):
        url = self.stock_timely_realtime_url.format(stock.id[2:])
        content = self.get_html(url, stock)
        stock_realtime_time_trades, last_close = ParseForThsUtils.parse_realtime_time_stock_trades(content, stock)
	return stock_realtime_time_trades, last_close
	


    def get_realtime_day_stock_trades(self, stock):
        url = self.stock_daily_realtime_url.format(stock.id[2:])
        content = self.get_html(url, stock)
        stock_realtime_day_trades = ParseForThsUtils.parse_realtime_line_stock_trades(content, stock, 'day')
        return stock_realtime_day_trades



    def get_realtime_week_stock_trades(self, stock):
        url = self.stock_weekly_realtime_url.format(stock.id[2:])
        content = self.get_html(url, stock)
        stock_realtime_week_trades = ParseForThsUtils.parse_realtime_line_stock_trades(content, stock, 'week')
        return stock_realtime_week_trades


    def get_realtime_month_stock_trades(self, stock):
        url = self.stock_monthly_realtime_url.format(stock.id[2:])
        content = self.get_html(url, stock)
        stock_realtime_month_trades = ParseForThsUtils.parse_realtime_line_stock_trades(content, stock, 'month')
        return stock_realtime_month_trades


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
    spider = StockDayIncForThsSpider()
    spider.get_all_stocks_realtime_trades()

