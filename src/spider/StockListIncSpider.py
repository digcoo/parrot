# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback

from utils.ParseUtil import *
from utils.SinaStockUtils import *
from vo.StockInfo import *
from dbs.GeodeClient import *

class StockListIncSpider:

    def __init__(self):
	self.stock_list_url='http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={0}&num={1}&sort=changepercent&asc=0&node={2}&symbol=&_s_r_a=page'
	self.size = 80
	self.geode_client = GeodeClient()

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

            if(jsonArray is not None and len(jsonArray) > 0):
		count += len(jsonArray)
		inc_stocks = []

                for i in range(0, len(jsonArray)):
                    symbol = jsonArray[i]['symbol']
                    code = jsonArray[i]['code']
                    name = jsonArray[i]['name']
		    stock = StockInfo()
		    stock.id = symbol
		    stock.code = code
		    stock.name = name
		    inc_stocks.append(stock)
                    print 'symbol=%s, code=%s, name=%s' % (symbol, code, name)
		
		inc_stocks = self.compose_inc_stocks(inc_stocks)

		self.geode_client.add_batch_stocks(inc_stocks)
	    return count

	except Exception, e:
	    traceback.print_exc()
	return 0

    def update_stocks_status(self):
	try:
	    com_stocks = []
	    all_stocks = GeodeClient.get_instance().query_all_stocks()
	    all_symbols = ParseUtil.parse_stock_symbol_list(all_stocks)
	    '''获取当天数据'''
	    current_stocks_day = SinaStockUtils.get_current_stock_days(all_symbols)
	    '''组合当天交易股票(suspend_stocks, market_stocks, re_market_stocks)'''
	    (suspend_stocks, market_stocks, re_market_stocks) = ParseUtil.compose_stocks_market(all_stocks, current_stocks_day)
	    com_stocks.extend(suspend_stocks)
	    com_stocks.extend(market_stocks)
	    GeodeClient.get_instance().add_batch_stocks(com_stocks)
	except Exception, e:
	    traceback.print_exc()

    def get_html(self, url):
        try:
	    response = urllib2.urlopen(url)
	    return response.read().decode("gbk")
        except Exception, e:
            traceback.print_exc()
        return ''

    def compose_inc_stocks(self, inc_stocks):
	local_stocks = self.geode_client.query_all_stocks()
	for inc_stock in inc_stocks:
	    for local_stock in local_stocks:
		if local_stock.id == inc_stock.id:
		    inc_stock.status = local_stock.status
	return inc_stocks


if __name__ == '__main__':
    spider = StockListIncSpider()
#    print spider.get_stock_list()
    print spider.update_stocks_status()

