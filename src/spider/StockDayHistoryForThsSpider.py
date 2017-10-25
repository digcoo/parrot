# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback

from utils.ObjectUtils import *
from utils.HttpUtils import *
from utils.ParseForThsUtils import *
from dbs.GeodeClient import *
'''
同花顺日交易历史
'''
class StockDayHistoryForThsSpider:

    def __init__(self):
	self.stock_timely_list_url = 'http://d.10jqka.com.cn/v6/time/hs_{0}/last.js'		#code
	self.stock_daily_list_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/01/{1}.js'		#code, year
	self.stock_weekly_list_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/11/last.js'		#code
	self.stock_monthly_list_url = 'http://d.10jqka.com.cn/v6/line/hs_{0}/21/last.js'	#code
	self.stock_detail_url = 'http://stockpage.10jqka.com.cn/{0}/'				#code


    def get_all_stocks_histories(self):
	all_stocks = GeodeClient.get_instance().query_all_stocks()
	all_stocks = ObjectUtils.dic_2_object(all_stocks)
	
#	self.get_all_stocks_days(all_stocks)
#	self.get_all_stocks_weeks(all_stocks)
	self.get_all_stocks_months(all_stocks)

    def get_all_stocks_days(self, all_stocks):
        if all_stocks is not None and len(all_stocks) > 0:
            for stock in all_stocks:
                self.get_stock_days(stock)
		break


    def get_stock_days(self, stock):
        try:
            stub_year = 2017
            url = self.stock_daily_list_url.format(stock.id[2:], stub_year)
            print 'get_stock_days, url = ' + url
            content = self.get_html(url, stock)
            stock_days = ParseForThsUtils.parse_stock_days(stock, content)
            while stock_days is not None and len(stock_days) > 0:

                LogUtils.info('collecting stock days symbol = ' + stock.id + ', year = ' + str(stub_year) + ', days_size = ' + str(len(stock_days)) + ', url = ' + url)

                #save todo
#               GeodeClient.get_instance().add_batch_stock_days(stock_days)

                time.sleep(3)
                stub_year -= 1
                url = self.stock_daily_list_url.format(stock.id[2:], stub_year)
                content = self.get_html(url, stock)
                stock_days = ParseForThsUtils.parse_stock_days(stock, content)

        except Exception, e:
            traceback.print_exc()
        return None


		

    def get_all_stocks_weeks(self, all_stocks):
        if all_stocks is not None and len(all_stocks) > 0:
            for stock in all_stocks:
		url = self.stock_weekly_list_url.format(stock.id[2:])
		content = self.get_html(url, stock)
		stock_weeks = ParseForThsUtils.parse_stock_days(stock, content)

		
                if stock_weeks is None or len(stock_weeks) == 0:
                    continue


		LogUtils.info('collecting stock weeks symbol = ' + stock.id + ', weeks_size = ' + str(len(stock_weeks))  + ', url = ' + url)

		#save weeks
#		GeodeClient.get_instance().add_batch_stock_weeks(stock_weeks)


    def get_all_stocks_months(self, all_stocks):
        if all_stocks is not None and len(all_stocks) > 0:
            for stock in all_stocks:
                url = self.stock_monthly_list_url.format(stock.id[2:])
                content = self.get_html(url, stock)
                stock_months = ParseForThsUtils.parse_stock_days(stock, content)
		
		if stock_months is None or len(stock_months) == 0:
		    continue
		
		LogUtils.info('collecting stock months symbol = ' + stock.id + ', months_size = ' + str(len(stock_months)) + ', url = ' + url)

                #save months
#		GeodeClient.get_instance().add_batch_stock_months(stock_months)


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
    spider = StockDayHistoryForThsSpider()
    spider.get_all_stocks_histories()

