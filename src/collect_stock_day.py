import traceback

from vo.StockInfo import *
from utils.TimeUtils import *
from utils.FileUtils import *
from dbs.GeodeClient import *
from dbs.MysqlClient import *
#from web.RecommendPoolServer import *
from spider.StockListIncSpider import *
from spider.StockDayIncSpider import *
from spider.PlateListIncForThsSpider import *
from spider.StockTimeIncSpider import *
from spider.StockTimeIncForEMSpider import *
from spider.StockTimeIncForSinaSpider import *
from spider.BusinessListIncSpider import *
from spider.BusinessDayIncSpider import *

def stock_list_inc_start():
    try:

        stock_list_inc_spider = StockListIncSpider()
        stock_list_inc_spider.get_stock_list()

    except Exception, e:
	traceback.print_exc()



def stock_day_inc_start():
    try:
	symbols = GeodeClient.get_instance().query_all_stock_symbols()
        stock_day_inc_spider = StockDayIncSpider(symbols, inc_persist = True)
        stock_day_inc_spider.get_allstocks_day()

    except Exception, e:
        traceback.print_exc()



def plate_list_inc_start():
    try:

	plate_list_spider = PlateListIncForThsSpider()
	plate_list = plate_list_spider.get_plate_list()
	plate_list_spider.get_all_plate_stocks(plate_list)

    except Exception, e:
	traceback.print_exc()


def stock_time_inc_start():

    try:

	symbols = GeodeClient.get_instance().query_all_stock_symbols()[:2]
        stock_time_inc_spider = StockTimeIncForSinaSpider(stock_analyzer=None, symbols=symbols, inc_persist=False, hit_persist=False, identify=None)
        stock_time_inc_spider.get_all_stocks_realtime_trades()

    except Exception, e:
        traceback.print_exc()



def business_day_inc_start():
    try:

#        business_list_spider = BusinessListIncSpider()
#        business_list = business_list_spider.get_business_list()

	all_business_list = MysqlClient.get_instance().query_all_business_list()
	business_day_spider  = BusinessDayIncSpider()
	business_day_spider.get_latest_business_days([business_info['id'] for business_info in all_business_list])

    except Exception, e:
        traceback.print_exc()


if __name__ == '__main__':
    try:

#	stock_list_inc_start()
#	stock_day_inc_start()
#	plate_list_inc_start()
#	stock_time_inc_start()
	business_day_inc_start()

    except Exception, e:
        traceback.print_exc()

