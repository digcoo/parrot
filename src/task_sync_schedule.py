#coding=utf-8

'''
同步数据入库
'''

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
from utils.SinaStockUtils import *

scheduler = BlockingScheduler()

#股票日交易列表:每个交易日15：10更新交易数据
@scheduler.scheduled_job('cron', id='stock_day_inc_spider', minute='30', day_of_week='0-4', hour='15')
def stock_day_inc_spider():

    try:

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

	plate_list_spider.get_all_plate_stocks(plate_list)

	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('rek_plate_stock_inc_spider take %s seconds' % (str(end - start), ))
	LogUtils.info('===============================rel_plate_stock_inc_spider end=============================================\n\n\n')




	symbols = GeodeClient.get_instance().query_all_stock_symbols()

	LogUtils.info('===============================stock_day_inc_spider start=============================================')
	start  = int(time.mktime(datetime.datetime.now().timetuple()))

	stock_day_inc_spider = StockDayIncSpider(symbols = symbols, inc_persist=True)
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

	stock_time_inc_spider = StockTimeIncSpider(stock_analyzer=None, symbols=symbols, inc_persist=True, hit_persist=False, identify=None)
	stock_time_inc_spider.get_all_stocks_realtime_trades()

	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('stock_time_inc_spider_for_ths take %s seconds' % (str(end - start), ))
	LogUtils.info('===============================stock_time_inc_spider_from_ths end=============================================\n\n\n')

    except Exception:
	traceback.print_exc()


scheduler.start()
