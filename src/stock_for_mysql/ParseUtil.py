# encoding=utf8  
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# import cPickle as pickle

from StockInfo import *
from StockDayInfo import *



class ParseUtil:

    def __init__(self):
	self.name = ''

    @staticmethod
    def parse_stock_day(content):
	stocks_day = []
	if content is not None:
	    lines = content.splitlines()
	    for i in range(0, len(lines)):
		stock_day = ParseUtil.compose_stock_day_info(lines[i].encode('utf-8'))
		stocks_day.append(stock_day)
#		print pickle.dumps(stock)
	return stocks_day

    @staticmethod
    def compose_stock_day_info(line):
	symbol = line[11: line.index('=')]
        line_data = line[line.index('"') + 1 : line.index(';') -1]
        split = line_data.split(',')
        stock = StockDayInfo()
	stock.symbol = symbol	#代码symbol
        stock.op = split[1]   #开盘价
        stock.close = split[3]   #当前价
	stock.high = split[4]   #最高价
	stock.low = split[5]   #最低价
	stock.buy1 = split[6]   #买一价
	stock.sell1 = split[7]   #卖一价
	stock.vol = split[8]   #成交量(股)
	stock.money = split[9]   #成交总金额(元)
	stock.buy1_vol = split[10]   #买一量(股)
        stock.sell1_vol = split[20]   #卖一量(股)
	stock.day = split[30] + ' ' + split[31]
	print line_data
	return stock

    @staticmethod
    def parse_stock_ids(stocks):
	ids = ''
	for stock in stocks:
	    ids += stock['symbol'] + ','

	ids = ids[0 : len(ids)-1]
	return ids


    @staticmethod
    def parse_stock_list(content):
	return ''
