# encoding=utf8  

import time
import urllib2
import demjson as json

import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

from StockInfo import *
from ParseUtil import *
from MysqlConn import *

class SpiderSingle:

    def __init__(self):
	self.stock_single_url = 'http://hq.sinajs.cn/list={0}'
	self.mysql_conn = MysqlConn()


    def get_stocks_day_single(self, symbols):
        try:
	    url = self.stock_single_url.format(symbols)
	    print url
	    content = self.get_html(url)
	    stocks_day = ParseUtil.parse_stock_day(content)
	    self.add_stocks_day(stocks_day)
        except Exception, e:
            print e
        return ''

    def get_html(self, url):
        try:
	    response = urllib2.urlopen(url)
	    return response.read().decode("gbk")
        except Exception, e:
            print e
        return ''


    def add_stocks_day(self, stocks_day):
	for stock_day in stocks_day:
	    self.mysql_conn.add_stock_day(stock_day)

    def get_allstocks_day(self):
	try:
	    page = 1
	    size = 50
	    stocks = self.mysql_conn.query_stock_page_list(page, size)
	    while(stocks is not None and len(stocks) > 0):
		stock_ids_str = ParseUtil.parse_stock_ids(stocks)
		stocks_day = self.get_stocks_day_single(stock_ids_str)
		self.add_stocks_day(stocks_day)
		
		page += 1
		stocks = self.mysql_conn.query_stock_page_list(page, size)
	except Exception, e:
	    print e
	    

spider = SpiderSingle()
spider.get_allstocks_day()
#print spider.get_stocks_day_single('sh603098,sh601006')


