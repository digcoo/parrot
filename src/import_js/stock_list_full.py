# encoding=utf8  

import time
import urllib2
import demjson as json

import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 


from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/vo')
path.append('/home/ubuntu/scripts/utils')


from StockInfo import *
from GeodeClient import *

class Spider:

    def __init__(self):
	self.stock_list_url='http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={0}&num={1}&sort=changepercent&asc=0&node={2}&symbol=&_s_r_a=page'
	self.size = 80
	self.geode_client = GeodeClient()

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
	    count += self.get_stock_exchange_list('new_stock')
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

            while(jsonArray is not None and len(jsonArray) > 0):
		print str(page) + ':' + str(len(jsonArray))
		
		count += len(jsonArray)
		all_stocks = []
                for i in range(0, len(jsonArray)):
                    symbol = jsonArray[i]['symbol']
                    code = jsonArray[i]['code']
                    name = jsonArray[i]['name']
		    stock = StockInfo()
		    stock.id = symbol
		    stock.name = name
		    all_stocks.append(stock)
#                    print 'symbol={0}, code={1}, name={2}'.format(symbol, code, name)

                all_stocks = self.compose_all_stocks(all_stocks)
               
		self.geode_client.add_batch_stocks(all_stocks)
 
		page += 1
		url = self.stock_list_url.format(page, self.size, exchange)
                content = self.get_html(url)
		jsonArray = json.decode(content)
		time.sleep(1)

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


    def compose_all_stocks(self, all_stocks):
        local_stocks = self.geode_client.query_all_stocks()
        for stock in all_stocks:
            for local_stock in local_stocks:
                if local_stock.id == stock.id:
                    stock.status = local_stock.status
        return all_stocks



spider = Spider()
print spider.get_stock_list()


