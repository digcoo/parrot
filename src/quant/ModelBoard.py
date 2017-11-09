# encoding=utf-8
from utils.BaseStockUtils import *
from utils.IndicatorUtils import *
from dbs.MysqlClient import *

import time
import traceback
import jsonpickle


'''
1、龙虎榜
'''
class ModelBoard:

    def __init__(self, todaystamp):
	self.todaystamp = todaystamp
        self.candidate_stocks = self.prepare_candidate_stocks()

    def prepare_candidate_stocks(self):
        candidate_stocks = {}
	board_stock_list = MysqlClient.get_instance().query_board_list_for_ndays(3)
        for board_stock in board_stock_list:
	    hit = self.Board(board_stock)
            if hit is not None:
                candidate_stocks[board_stock['s_symbol']] = hit
        return candidate_stocks


    def Board(self, board_stock):
	return ('Board', )


    def match(self, realtime_stock_day):

	try:

            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None

            is_hit = True
	    return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-' +  str(0), )

            is_hit = is_hit & (realtime_stock_day.high > realtime_stock_day.last_close)                #当前价高于昨日收盘价

            if is_hit:
#		print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" + realtime_stock_day.symbol
                return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-' +  str(0), )

	except Exception, e:
	    traceback.print_exc()

	return None



