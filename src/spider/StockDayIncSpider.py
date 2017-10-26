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
from analyzer.StockDayAnalyzer import *
from dbs.RedisClient import *
from utils.CommonUtils import *
from utils.LogUtils import *
from dto.CacheData import *

class StockDayIncSpider:

    def __init__(self, stock_analyzer, symbols, inc_persist, hit_persist):
	self.stock_single_url = 'http://hq.sinajs.cn/list={0}'
	self.stock_timely_realtime_url_for_ths = 'http://d.10jqka.com.cn/v6/time/hs_{0}/today.js'               #code
	self.stock_detail_url_for_ths = 'http://stockpage.10jqka.com.cn/{0}/'                   #code(stock.id[2:])
	self.symbols = symbols
	self.stock_analyzer = stock_analyzer
	self.inc_persist = inc_persist
	self.hit_persist = hit_persist
	self.redis_client = RedisClient()
	self.stub_time = '12:00:00'
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
#		stock_ids_str = ParseUtil.parse_stock_ids(temp_symbols)
#		stocks_day = self.get_stocks_day_single(stock_ids_str)
	
		if self.stock_analyzer is not None:
		    batch_hit = self.analyze(stocks_day)
		    if  batch_hit is not None and len(batch_hit) > 0:
			hit_list.extend(batch_hit)

		#日线数据持久存储
		if self.inc_persist:
  		    GeodeClient.get_instance().put_stocks_day(stocks_day)
		
		page += 1
                start = (page -1) * size
                end = page*size if page * size < len(self.symbols) else len(self.symbols)
                temp_symbols = self.symbols[start : end]
	    
	    #推荐数据持久存储
	    if len(hit_list) > 0 and self.hit_persist:
		self.redis_client.put_today_rec(hit_list, 'day')

#	    if not TimeUtils.is_after(self.stub_time):
#	        CacheData.set_hit_symbols(hit_list)
#		LogUtils.hit_to_file(json.encode(hit_list))
#	    else:
#		LogUtils.info('morn hit symbols size = ' + str(CacheData.morn_hit_symbols))

	    LogUtils.info('stock day recommend stock cnt = ' + str(len(hit_list)))

	except Exception, e:
	    traceback.print_exc()


    def analyze(self, stocks_day):
	try:
	    if stocks_day is not None:
		batch_hit = []
        	for stock_day in stocks_day:
        	    hit = self.stock_analyzer.match(stock_day)
            	    if hit is not None and (not TimeUtils.is_after(self.stub_time) or len(CacheData.morn_hit_symbols) == 0 or hit[0] in CacheData.morn_hit_symbols):
                	batch_hit.append(hit)
            	return batch_hit
	except Exception, e:
	    traceback.print_exc()
	return None
	
if __name__ == '__main__':

    symbols = GeodeClient.get_instance().query_all_stock_symbols()

    symbols = CommonUtils.filter_symbols(symbols)

    symbols = list(filter(lambda x: x == 'sh600330', symbols))

    stock_analyzer = StockDayAnalyzer(symbols, TimeUtils.get_current_datestamp())

    spider = StockDayIncSpider(stock_analyzer=stock_analyzer, symbols=symbols, inc_persist=False, hit_persist=False)

    spider.get_allstocks_day()
