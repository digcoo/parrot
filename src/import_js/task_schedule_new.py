#coding=utf-8
from apscheduler.schedulers.blocking import BlockingScheduler
from StockListIncSpider import *
from StockDayIncSpider import *
import time


class SpiderStarter:

    def __init__(self):
	self.scheduler = BlockingScheduler()
	self.stock_analyzer = None


    #初始化数据缓存:每日更新
    def stock_days_cache_task(self):
        print 'stock_days_cache start....'
        self.stock_analyzer = StockAnalyzer()
        print 'stock_days_cache end....'


    #股票列表更新:每个交易日9：25更新股票列表
    def stock_list_inc_spider_task(self):
        print 'stock_list_inc_spider start....'
        list_spider = StockListIncSpider()
        list_spider.get_stock_list()
        print 'stock_list_inc_spider end....'


    #股票日交易列表:每个交易日15：10更新交易数据
    def stock_day_inc_spider_task(self):
        print 'stock_day_inc_spider start....'
        day_inc_spider = StockDayIncSpider(None, is_persist=True)
        day_inc_spider.get_allstocks_day()
        print 'stock_day_inc_spider end....'



    def stock_day_realtime_spider_task(self):
	print 'stock_day_realtime_spider start....'
	if self.stock_analyzer is None:
	    self.stock_analyzer = StockAnalyzer()
        spider = StockDayIncSpider(self.stock_analyzer)
        spider.get_allstocks_day()
        print 'stock_day_realtime_spider end....'

    def start(self):
	try:
	    self.scheduler.add_job(self.stock_days_cache_task, 'cron', minute='0', day_of_week='0-4', hour='9', id='stock_days_cache')
	    self.scheduler.add_job(self.stock_list_inc_spider_task, 'cron', minute='25', day_of_week='0-4', hour='9')
	    self.scheduler.add_job(self.stock_day_inc_spider_task, id='stock_day_inc_spider', minute='10', day_of_week='0-4', hour='15')
	    self.scheduler.add_job(self.stock_day_realtime_spider_task, 'cron', second='*/1', day_of_week='0-4', hour='9-12,13-22', max_instances=1, id='stock_day_realtime_spider')
            self.scheduler.start()
	except Exception, e:
	    print e


if __name__ == '__main__':
    spider= SpiderStarter()
    spider.start()
#    spider = StockDayIncSpider(None)
#    spider.get_allstocks_day()

