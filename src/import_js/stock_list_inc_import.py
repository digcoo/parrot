#encoding=utf-8

import gemfire
from sys import path
path.append('/home/ubuntu/scripts/utils')
import jsonpickle
from GeodeClient import *
from TushareUtils import *

geode_client = GeodeClient()

local_symbols = geode_client.query_all_stock_symbols()
print len(local_symbols)
tushare_stocks = TushareUtils.query_all_stocks()
print len(tushare_stocks)

inc_stocks = []
for tushare_stock in tushare_stocks:
    if tushare_stock.id not in local_symbols:
	inc_stocks.append(tushare_stock)

#geode_client.put_all_stocks(inc_stocks)

print 'inc stock size = ' + str(len(inc_stocks))
print jsonpickle.encode(inc_stocks)
