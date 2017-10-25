#coding=utf-8
from apscheduler.schedulers.blocking import BlockingScheduler
from spider.StockListIncSpider import *
from spider.StockDayIncSpider import *
from spider.StockWeekIncSpider import *
from spider.StockMonthIncSpider import *
from spider.PlateListIncForThsSpider import *
from spider.PlateDayIncForThsSpider import *
from spider.StockTimeIncSpider import *
import time
from utils.LogUtils import *
from utils.CommonUtils import *
from utils.SinaStockUtils import *
from dto.CacheData import *

scheduler = BlockingScheduler()
global stock_day_analyzer
stock_day_analyzer = None

global stock_time_analyzer
stock_time_analyzer = None

global is_new_day
is_new_day = False		#是否新的交易日

global symbols
symbols = None

global stock_day_inc_spider
stock_day_inc_spider = None

global stock_time_inc_spider
stock_time_inc_spider = None


global todaystamp
todaystamp = 0

#初始化数据缓存:每日更新
@scheduler.scheduled_job('cron', hour='9', day_of_week='0-4')
def stock_days_cache():

    global is_new_day
    is_new_day = False

#    if not SinaStockUtils.is_market_open():
#        return

    LogUtils.info('===============================stock_days_cache start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    global symbols
    symbols = GeodeClient.get_instance().query_all_stock_symbols()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_days_cache take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================stock_days_cache end=============================================\n\n\n')



#股票日交易列表:每个交易日15：10更新交易数据
@scheduler.scheduled_job('cron', id='stock_day_inc_spider', minute='45', day_of_week='0-4', hour='15')
def stock_day_inc_spider():

    if not SinaStockUtils.is_market_open():
        return


    LogUtils.info('===============================stock_list_inc_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    stock_list_inc_spider = StockListIncSpider()
    stock_list_inc_spider.get_stock_list()

    stock_list_inc_spider.update_stocks_status()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_list_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================stock_list_inc_spider end=============================================\n\n\n')



    LogUtils.info('===============================plate_list_inc_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    plate_list_spider = PlateListIncForThsSpider()
    plate_list = plate_list_spider.get_plate_list()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('plate_list_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================plate_list_inc_spider end=============================================\n\n\n')




    LogUtils.info('===============================rel_plate_stock_inc_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    plate_list_spider.get_plate_list()
    plate_list_spider.get_all_plate_stocks(plate_list)

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('rek_plate_stock_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================rel_plate_stock_inc_spider end=============================================\n\n\n')




    symbols = GeodeClient.get_instance().query_all_stock_symbols()

    LogUtils.info('===============================stock_day_inc_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    stock_day_inc_spider = StockDayIncSpider(stock_analyzer=None, symbols = symbols, is_persist=True)
    stock_day_inc_spider.get_allstocks_day()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_day_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================stock_day_inc_spider end=============================================\n\n\n')
    


    LogUtils.info('===============================stock_week_inc_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    week_inc_spider = StockWeekIncSpider()
    week_inc_spider.get_allstocks_week()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_week_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================stock_week_inc_spider end=============================================\n\n\n')



    LogUtils.info('===============================stock_month_inc_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    month_inc_spider = StockMonthIncSpider()
    month_inc_spider.get_allstocks_month()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_month_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================stock_month_inc_spider end=============================================\n\n\n')



    LogUtils.info('===============================plate_day_inc_spider[week, month] start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    plate_day_inc_spider = PlateDayIncForThsSpider()
    plate_day_inc_spider.get_all_plates_realtime_trades()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('plate_day_inc_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================plate_day_inc_spider[week, month] end=============================================\n\n\n')



    LogUtils.info('===============================stock_time_inc_spider_from_ths start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    stock_time_inc_spider = StockTimeIncSpider(stock_analyzer=None, symbols=symbols, is_persist=True)
    stock_time_inc_spider.get_all_stocks_realtime_trades()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_time_inc_spider_for_ths take %s seconds' % (str(end - start), ))
    LogUtils.info('===============================stock_time_inc_spider_from_ths end=============================================\n\n\n')



#股票日交易列表:每个交易日9点同步实时交易数据
@scheduler.scheduled_job('cron', id='stock_day_realtime_spider', second='*/60', day_of_week='0-4', hour='9-23', max_instances=1)
def stock_day_realtime_spider():

    if not SinaStockUtils.is_market_open():
        return

    with_gem = False

    global is_new_day
    if not is_new_day:
	LogUtils.info('=====================init_current_daily_data start=============================================')
	start  = int(time.mktime(datetime.datetime.now().timetuple()))

        is_new_day = True

        #更新当前时间戳
        global todaystamp
        todaystamp = TimeUtils.get_current_datestamp()

	#初始化当前股票列表
	global symbols
	symbols = GeodeClient.get_instance().query_all_stock_symbols()
	if not with_gem:
	    symbols = CommonUtils.filter_symbols(symbols)

	#初始化股票今日开盘情况(包括今日停盘、今日复盘的股票)
	CacheData.init()

        #初始化分析器
        global stock_day_analyzer
        stock_day_analyzer = StockDayAnalyzer(symbols = symbols, todaystamp=todaystamp)


        #初始化(分时)分析器
        global stock_time_analyzer
        stock_time_analyzer = StockTimeAnalyzer(symbols = symbols, todaystamp=todaystamp)


	#初始化实时爬虫器
	global stock_day_inc_spider
	stock_day_inc_spider = StockDayIncSpider(stock_analyzer=stock_day_analyzer, symbols = symbols, is_persist=False)


        #初始化实时(分时)爬虫器
        global stock_time_inc_spider
        stock_time_inc_spider = StockTimeIncSpider(stock_analyzer=stock_time_analyzer, symbols = symbols, is_persist=False)
	stock_time_inc_spider.get_all_stocks_realtime_trades()		#启动分时爬虫

	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('init_current_daily_data take %s seconds' % (str(end - start), ))
	LogUtils.info('=====================init_current_daily_data end=============================================\n\n\n')


    LogUtils.info('=====================stock_day_realtime_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    stock_day_inc_spider.get_allstocks_day()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_day_realtime_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('=====================stock_day_realtime_spider end=============================================\n\n\n')



#股票分时交易列表:每个交易日9点同步实时交易数据
@scheduler.scheduled_job('cron', id='stock_time_realtime_spider', minute='*/5', day_of_week='0-4', hour='9-14', max_instances=1)
def stock_time_realtime_spider():

    if not SinaStockUtils.is_market_open():
        return

    LogUtils.info('=====================stock_time_realtime_spider start=============================================')
    start  = int(time.mktime(datetime.datetime.now().timetuple()))

    '''
    #更新当前时间戳
    global todaystamp
    todaystamp = TimeUtils.get_current_datestamp()


    global with_gem
    with_gem = False

    #初始化当前股票列表
    global symbols
    symbols = GeodeClient.get_instance().query_all_stock_symbols()
    if not with_gem:
        symbols = CommonUtils.filter_symbols(symbols)


    #初始化(分时)分析器
    global stock_time_analyzer
    stock_time_analyzer = StockTimeAnalyzer(symbols = symbols, todaystamp=todaystamp)


    #初始化实时爬虫器
    global stock_time_inc_spider
    stock_time_inc_spider = StockTimeIncSpider(stock_analyzer=stock_time_analyzer, symbols = symbols, is_persist=False)

    '''

    global stock_time_inc_spider
    if stock_time_inc_spider is not None:
	stock_time_inc_spider.get_all_stocks_realtime_trades()

    end  = int(time.mktime(datetime.datetime.now().timetuple()))
    LogUtils.info('stock_time_realtime_spider take %s seconds' % (str(end - start), ))
    LogUtils.info('=====================stock_time_realtime_spider end=============================================\n\n\n')


scheduler.start()

'''
if __name__ == '__main__':
    spider = StockDayIncSpider(None)
    spider.get_allstocks_day()
'''
