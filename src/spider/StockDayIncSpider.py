# encoding=utf8  
import time
import urllib2
import jsonpickle as json
import traceback
from utils.HttpUtils import *
from vo.StockInfo import *
from utils.ParseUtil import *
from utils.ParseForThsUtils import *
from dbs.GeodeClient import *
from utils.CommonUtils import *
from utils.LogUtils import *
from utils.SinaStockUtils import *

class StockDayIncSpider:

    def __init__(self, symbols, inc_persist):
	self.stock_single_url = 'http://hq.sinajs.cn/list={0}'
	self.symbols = symbols
	self.inc_persist = inc_persist
	LogUtils.info('stock_day_inc_spider init finish...')

    def get_stocks_day_single(self, symbols):
        try:
	    url = self.stock_single_url.format(symbols)
	    content = self.get_html(url)
	    return ParseUtil.parse_stock_day(content)
        except Exception, e:
            traceback.print_exc()
        return None

    def get_html(self, url):
        try:
	    response = urllib2.urlopen(url)
	    return response.read().decode("gbk")
        except Exception, e:
            traceback.print_exc()
        return None


    def get_allstocks_day(self):
	try:
	    hit_list = []
	    page = 1
	    size = 50
	    start = (page -1) * size
	    end = page*size if page * size < len(self.symbols) else len(self.symbols)
	    temp_symbols = self.symbols[start : end]
	    while(len(temp_symbols) > 0):
		stocks_day = SinaStockUtils.get_current_stock_days(temp_symbols)
	
		#日线数据持久存储
		if self.inc_persist:
  		    GeodeClient.get_instance().put_stocks_day(stocks_day)
		
		page += 1
                start = (page -1) * size
                end = page*size if page * size < len(self.symbols) else len(self.symbols)
                temp_symbols = self.symbols[start : end]
	    
	    LogUtils.info('stock day recommend stock cnt = ' + str(len(hit_list)))

	except Exception, e:
	    traceback.print_exc()


if __name__ == '__main__':

    symbols = GeodeClient.get_instance().query_all_stock_symbols()

    symbols = CommonUtils.filter_symbols(symbols)

    symbols = list(filter(lambda x: x == 'sh600330', symbols))

    stock_analyzer = StockDayAnalyzer(symbols, TimeUtils.get_current_datestamp())

    spider = StockDayIncSpider(stock_analyzer=stock_analyzer, symbols=symbols, inc_persist=False, hit_persist=False)

    spider.get_allstocks_day()
