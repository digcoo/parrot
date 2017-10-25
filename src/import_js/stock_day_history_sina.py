from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/vo')
path.append('/home/ubuntu/scripts/utils')

from StockInfo import *
from ParseUtil import *
from GeodeClient import *


import urllib2
import time
import jsonpickle as json


class StockDayHistorySpider:

    def __init__(self):
	self.stock_day_url = 'http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{0}.phtml?year={1}&jidu={2}'
        self.geode_client = GeodeClient()


    def get_stock_days_history(self, symbol):
	count = 0
        try:
            code = symbol[2 : len(symbol)]
	    start_year = 2010
	    end_year = 2017
	    start_quarter = 1
	    end_quarter = 4
	    for year in range(start_year, end_year + 1):
		for quarter in range(start_quarter, end_quarter + 1):
		    url = self.stock_day_url.format(code, year, quarter)
		    content = self.get_html(url)
		    stock_days = ParseUtil.compose_stock_days_form_sina(symbol, content)
		    self.add_stock_days_page(stock_days)
		    count += len(stock_days)
		    if len(stock_days) == 0:
			print 'get no data : url = ' + url
		    time.sleep(2)

        except Exception, e:
            print e
        return count

    def get_allstocks_day(self):
        try:
#            symbols = self.geode_client.query_all_stock_symbols()
#	    symbols = ['sh600760','sh600275','sh600390','sh600381','sh600225','sh600721','sh600696','sh600866','sh600817','sh600767','sh600860','sh600675','sh600149','sh600732','sh600680','sh601519','sh601005','sh600793','sh600747','sh600733','sh600725','sh600701','sh600636','sh600581','sh600346','sh600228','sh600145','sz300706','sh600375','sh600540','sh600815','sh600539','sh600710','sh600301','sh600844','sh600339','sh600234','sh600603','sh600877','sh600091','sh600247','sh600179','sh601106','sh600112','sh600608','sh600319','sh600265','sh600847','sh600403','sh600423','sh601558','sh600401','sh600212','sh600306','sh600520','sh600425','sh601918','sh600121','sh600654','sh600556','sh600230','sh600546','sh603106','sh603103','sh603055','sh601086','sh600806','sh600432','sz300705','sz300703','sz300702','sz300654','sz002902','sz002901','sz002900','sh603963','sh603922','sh603619','sh603533','sh603378','sh603367','sh603363','sh603157','sh603136']
	    symbols = ['sh600636','sh600581','sh600346','sh600228','sh600145','sz300706','sh600375','sh600540','sh600815','sh600539','sh600710','sh600301','sh600844','sh600339','sh600234','sh600603','sh600877','sh600091','sh600247','sh600179','sh601106','sh600112','sh600608','sh600319','sh600265','sh600847','sh600403','sh600423','sh601558','sh600401','sh600212','sh600306','sh600520','sh600425','sh601918','sh600121','sh600654','sh600556','sh600230','sh600546','sh603106','sh603103','sh603055','sh601086','sh600806','sh600432','sz300705','sz300703','sz300702','sz300654','sz002902','sz002901','sz002900','sh603963','sh603922','sh603619','sh603533','sh603378','sh603367','sh603363','sh603157','sh603136']
	    print len(symbols)
	    fail_symbols = []
	    flag = False
	    symbol_cnt = 0
            for symbol in symbols:
		symbol_cnt += 1
		print 'travel symbol = ' + symbol + ', has travel symbol_cnt = ' + str(symbol_cnt)
#		if symbol == 'sz002658':
#		if symbol_cnt > 2425:
#		    flag = True

#		if flag == False:
#		    continue	

		count = self.get_stock_days_history(symbol)
		print 'collect symbol = ' + symbol + ', count = ' + str(count)
		if count == 0:
		    fail_symbols.append(symbol)
	    print fail_symbols
 
        except Exception, e:
            print e


    def get_allstocks_day_reverse(self):
        try:
            symbols = self.geode_client.query_all_stock_symbols()
            fail_symbols = []
            symbol_cnt = 0
	    total = len(symbols)
	    for cursor in range(0, total):
		symbol = symbols[total - cursor - 1]
                symbol_cnt += 1
                print 'travel symbol = ' + symbol + ', has travel symbol_cnt = ' + str(symbol_cnt)

                count = self.get_stock_days_history(symbol)
                print 'collect symbol = ' + symbol + ', count = ' + str(count)
                if count == 0:
                    fail_symbols.append(symbol)
            print fail_symbols

        except Exception, e:
            print e



    def add_stock_days_page(self, stock_days):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(stock_days) else (len(stock_days) + 1)
        temp_stock_days = stock_days[start : end]
        while(len(temp_stock_days) > 0):
	    self.geode_client.put_stocks_day(temp_stock_days)
	    page += 1	    
	    start = (page -1) * size
            end = page*size if page * size < len(stock_days) else (len(stock_days) + 1)
            temp_stock_days = stock_days[start : end]

    def get_html(self, url):
	response = None
        try:
            response = urllib2.urlopen(url)
            return response.read().decode("gbk")
        except urllib2.URLError as e:
	    if hasattr(e, 'code') and e.code != '200':
		time.sleep(5 * 60)
                response = urllib2.urlopen(url)
                return response.read().decode("gbk")
            print e
	finally:
  	    if response:
                response.close()
        return ''


if __name__ == '__main__':
    spider = StockDayHistorySpider()
    spider.get_allstocks_day()
    #print spider.get_stock_days_history('sh601101')




