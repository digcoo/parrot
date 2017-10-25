# encoding=utf8  

import time
import urllib2
import demjson as json

import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 
from StockInfo import *
from MysqlConn import *

class Spider:

    def __init__(self):
	self.stock_list_url='http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={0}&num={1}&sort=changepercent&asc=0&node={2}&symbol=&_s_r_a=page'
	self.size = 80
	self.mysql_conn = MysqlConn()

    def get_stock_page_list(self, page):
	try:
	    return ''	    
	except Exception, e:
	    print e
	return ''

    def get_stock_list(self):
	try:
	    count = self.get_stock_exchange_list('sh_a')
	    count += self.get_stock_exchange_list('sz_a')
	    print count
	except Exception, e:
            print e
	return ''

    def get_stock_exchange_list(self, exchange):
	
	count = 0

	try:

	    page = 1
            url = self.stock_list_url.format(page, self.size, exchange)
            content = self.get_html(url)
	    jsonArray = json.decode(content)

            if(jsonArray is not None and len(jsonArray) > 0):
		count += len(jsonArray)

                for i in range(0, len(jsonArray)):
                    symbol = jsonArray[i]['symbol']
                    code = jsonArray[i]['code']
                    name = jsonArray[i]['name']
		    stock = StockInfo()
		    stock.symbol = symbol
		    stock.code = code
		    stock.name = name
		    self.mysql_conn.add_stock(stock)
                    print 'symbol={0}, code={1}, name={2}'.format(symbol, code, name)

	    return count

	except Exception, e:
	    print e
	return 0

    def get_html(self, url):
        try:
	    response = urllib2.urlopen(url)
	    return response.read().decode("gbk")
        except Exception, e:
            print e
        return ''

spider = Spider()
print spider.get_stock_list()


