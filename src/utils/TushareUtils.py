#encoding=utf-8
import traceback
import tushare as ts
import jsonpickle
from sys import path
path.append('/home/ubuntu/scripts/vo')

from StockInfo import *


class TushareUtils:

    @staticmethod
    def query_all_stocks():
	try:
	    all_stocks = ts.get_stock_basics()
	    codes = list(all_stocks.index)
	    stocks = []
	    for code in codes:
		stock = StockInfo()
		if code.startswith('6'):
		    stock.id = 'sh' + code
		else:
		    stock.id = 'sz' + code
		stock.name =  all_stocks.loc['000001',['name']]['name']
		stocks.append(stock)
	    return stocks
	except Exception, e:
	    traceback.print_exc()
	return None

if __name__ == '__main__':
    TushareUtils.query_all_stock_symbols()
