#coding=utf-8
from apscheduler.schedulers.blocking import BlockingScheduler
from spider.StockListIncSpider import *
from spider.StockDayIncSpider import *
from spider.StockWeekIncSpider import *
from spider.StockMonthIncSpider import *
from spider.PlateListIncForThsSpider import *
from spider.PlateDayIncForThsSpider import *
import time
from utils.LogUtils import *
from utils.CommonUtils import *
from utils.SinaStockUtils import *
from dto.CacheData import *
from dbs.GeodeClient import *

scheduler = BlockingScheduler()

global stock_day_analyzer
stock_day_analyzer = None

global is_new_day
is_new_day = True		#是否新的交易日

global symbols
symbols = None

global stock_day_inc_spider
stock_day_inc_spider = None


global todaystamp
todaystamp = 0

#初始化数据缓存:每日更新
@scheduler.scheduled_job('cron', id='task_new_day_init', hour='9', day_of_week='0-4')
def task_new_day_init():

    try:

	LogUtils.info('===============================task_new_day_init start=============================================')
	start  = int(time.mktime(datetime.datetime.now().timetuple()))


	global is_new_day
	is_new_day = True


	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('stock_days_cache take %s seconds' % (str(end - start), ))
	LogUtils.info('===============================stock_days_cache end=============================================\n\n\n')

    except Exception, e:
	traceback.print_exc()


#股票日交易列表:每个交易日9点同步实时交易数据
@scheduler.scheduled_job('cron', id='stock_day_realtime_spider', second='*/60', day_of_week='0-4', hour='9-23', max_instances=1)
def stock_day_realtime_spider():

    try:

	if not SinaStockUtils.is_market_open():
	    return

	with_gem = False

	global is_new_day
	if is_new_day:
	    LogUtils.info('=====================init_current_daily_data start=============================================')
	    start  = int(time.mktime(datetime.datetime.now().timetuple()))

	    is_new_day = False

	    #更新当前时间戳
	    global todaystamp
	    todaystamp = TimeUtils.get_current_datestamp()

	    #初始化当前股票列表
	    global symbols
	    symbols = GeodeClient.get_instance().query_all_stock_symbols()
	    if not with_gem:
	        symbols = CommonUtils.filter_symbols(symbols)[:10]

 	    #初始化股票今日开盘情况(包括今日停盘、今日复盘的股票)
	    CacheData.init()

            #初始化分析器
	    global stock_day_analyzer
	    stock_day_analyzer = StockDayAnalyzer(symbols = symbols, todaystamp=todaystamp)


   	    #初始化实时爬虫器
	    global stock_day_inc_spider
	    stock_day_inc_spider = StockDayIncSpider(stock_analyzer=stock_day_analyzer, symbols = symbols, inc_persist=False, hit_persist=False)


	    end  = int(time.mktime(datetime.datetime.now().timetuple()))
	    LogUtils.info('init_current_daily_data take %s seconds' % (str(end - start), ))
	    LogUtils.info('=====================init_current_daily_data end=============================================\n\n\n')


	LogUtils.info('=====================stock_day_realtime_spider start=============================================')
	start  = int(time.mktime(datetime.datetime.now().timetuple()))

	stock_day_inc_spider.get_allstocks_day()

	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('stock_day_realtime_spider take %s seconds' % (str(end - start), ))
	LogUtils.info('=====================stock_day_realtime_spider end=============================================\n\n\n')

    except Exception, e:
	traceback.print_exc()


scheduler.start()

