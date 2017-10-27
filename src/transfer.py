import traceback

from vo.StockInfo import *
from utils.TimeUtils import *
from utils.FileUtils import *
from dbs.GeodeClient import *
#from web.RecommendPoolServer import *
from spider.StockListIncSpider import *
from spider.PlateListIncForThsSpider import *
from spider.StockTimeIncSpider import *


def stock_list_inc_start():
    try:

        stock_list_inc_spider = StockListIncSpider()
        stock_list_inc_spider.get_stock_list()

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

	symbols = GeodeClient.get_instance().query_all_stock_symbols()
        stock_time_inc_spider = StockTimeIncSpider(stock_analyzer=None, symbols=symbols, inc_persist=True, hit_persist=True, identify=None)
        stock_time_inc_spider.get_all_stocks_realtime_trades()

    except Exception, e:
        traceback.print_exc()




if __name__ == '__main__':
    try:

#        stock_list_inc_start()
#	plate_list_inc_start()
	stock_time_inc_start()

    except Exception, e:
        traceback.print_exc()

