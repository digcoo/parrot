# encoding=utf8  

import time
import datetime
import traceback
import jsonpickle
import copy

from vo.StockInfo import *
from vo.StockDayInfo import *
from utils.LogUtils import *

from bs4 import BeautifulSoup

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
		if stock_day is not None and stock_day.vol > 0 and stock_day.close > 0:
		    stocks_day.append(stock_day)
	return stocks_day

    #新浪每日成交价格解析
    @staticmethod
    def compose_stock_day_info(line):
	try:
            symbol = line[11: line.index('=')]
            line_data = line[line.index('"') + 1 : line.index(';') -1]
            split = line_data.split(',')
            stock = StockDayInfo()
            stock.id = symbol + split[30].strip().replace('-', '')
            stock.symbol = symbol   #代码symbol
            stock.op = float(split[1])   #开盘价
            stock.last_close = float(split[2])   #昨日收盘价
            stock.close = float(split[3])   #当前价
            stock.high = float(split[4])   #最高价
            stock.low = float(split[5])   #最低价
            stock.buy1 = float(split[6])   #买一价
            stock.sell1 = float(split[7])   #卖一价
            stock.vol = float(split[8])   #成交量(股)
            stock.money = float(split[9])   #成交总金额(元)
            stock.buy1_vol = float(split[10])   #买一量(股)
            stock.sell1_vol = float(split[20])   #卖一量(股)
            stock.day = int(time.mktime(time.strptime(split[30].strip(), "%Y-%m-%d")))
#           stock.day = datetime.datetime.strptime(split[30].strip(), "%Y-%m-%d").date()
	    if float(split[32]) == 0:
		stock.status = 'on_market'
	    elif float(split[32]) == 3:
		stock.status = 'suspend'
	    elif float(split[32]) == -2:
		stock.status = 'no_market'
            return stock
	except Exception, e:
	    LogUtils.info('[ParseUtils.compose_stock_day_info] stock_day no data, ' + line)
#	    traceback.print_exc()
	return None

    #新浪历史价格解析
    @staticmethod
    def compose_stock_days_form_sina(symbol, html_data):
        stock_days = []
	soup = BeautifulSoup(html_data)
	tables = soup.find_all('table')	
	target_table = None
	for table in tables:
	    if table.get('id') == 'FundHoldSharesTable':
		target_table = table
	if target_table == None:
	    return stock_days
	trs = target_table.find_all('tr')
	target_trs = trs[2:]
	for tr in target_trs:
            stock_day = StockDayInfo()
	    tds = tr.find_all('td')
	    stock_day.day = int(time.mktime(time.strptime(tds[0].get_text().strip(), "%Y-%m-%d")))
	    stock_day.op = float(tds[1].get_text().strip())
	    stock_day.high = float(tds[2].get_text().strip())
	    stock_day.close = float(tds[3].get_text().strip())
	    stock_day.low = float(tds[4].get_text().strip())
	    stock_day.vol = float(tds[5].get_text().strip())
	    stock_day.money = float(tds[6].get_text().strip())
	    stock_day.symbol = symbol
	    stock_day.id = symbol + tds[0].get_text().strip().replace('-', '')
	    stock_days.append(stock_day)
	return stock_days


    @staticmethod
    def parse_stock_ids(stock_keys):
	ids= ''
	for stock_key in stock_keys:
	    ids += stock_key + ','
	ids = ids[0 : len(ids)-1]
	return ids


    @staticmethod
    def parse_stock_symbol_list(stocks):
	if stocks is not None and len(stocks) > 0:
	    symbols = []
	    for stock in stocks:
		symbols.append(stock.id)
	    return symbols
	return None


    @staticmethod
    def compose_stocks_market(all_stocks, current_stocks_day):
        market_stocks = []
        re_market_stocks = []
        suspend_stocks = []

	market_symbols = ParseUtil.compose_market_stock_symbols(current_stocks_day)

        for stock in all_stocks:
            if stock.id not in market_symbols:
		stock.status = 'suspend'
                suspend_stocks.append(stock)
	    else:
		if stock.status == 'suspend':
		    re_market_stocks.append(stock)
		stock.status = 'on_market'
		market_stocks.append(stock)

        return (suspend_stocks, market_stocks, re_market_stocks)

    @staticmethod
    def compose_symbols(suspend_stocks, market_stocks, re_market_stocks):
        suspend_symbols = []
        market_symbols = []
        re_market_symbols = []
        for stock in suspend_stocks:
            suspend_symbols.append(stock.id)

        for stock in market_stocks:
            market_symbols.append(stock.id)

        for stock in re_market_stocks:
            re_market_symbols.append(stock.id)
        return (suspend_symbols, market_symbols, re_market_symbols)


    @staticmethod
    def compose_market_stock_symbols(current_stocks_day):
	market_symbols = []
	for stock_day in current_stocks_day:
	    market_symbols.append(stock_day.symbol)
	return market_symbols

    '''  转换一只股票最近2天的分时交易 '''
    @staticmethod
    def compose_stock_time_trades_map(hist_time_trades_map, today_time_trades_map):
	remain_days = 4
	final_time_trades_map = {}
	keys = today_time_trades_map.keys()
	if hist_time_trades_map is None:
	    return today_time_trades_map
	else:
	    hist_time_trades_map[today_time_trades_map.keys()[0]] = today_time_trades_map.values()[0]
	    day_stamps_uni = hist_time_trades_map.keys()
	    day_stamps = ParseUtil.transfer_unicodes_ints(day_stamps_uni)
	    day_stamps = sorted(day_stamps)
	    day_stamps.reverse()
	    latest_day_stamps = day_stamps[:min(remain_days, len(day_stamps))]
	    latest_day_stamps.reverse()
	    for day_stamp in latest_day_stamps:
	        final_time_trades_map[day_stamp] = hist_time_trades_map.get(unicode(day_stamp))
	    return final_time_trades_map

    @staticmethod
    def transfer_unicodes_ints(unicodes):
	if unicodes is not None:
	    values = []
	    for uni in unicodes:
		values.append(int(str(uni)))
	    return values
	return None

    #将数据库的日分时交易的map转换
    '''
    {'symbol1':{
	'date_stamp1':[],
	'date_stamp2':[]
	},
     'symbol2':{
        'date_stamp1':[],
        'date_stamp2':[]
        }
    }

    --->>>

    {'symbol1':[],
     'symbol2':[]
    }

    '''
    @staticmethod
    def compose_stock_times_from_daytimes_map(stocks_daytimes_map):
	allstocks_times_map = {}
	for symbol in stocks_daytimes_map.keys():
	    stock_daytimes_map = stocks_daytimes_map.get(symbol)
	    stock_all_daytimes = []
	    for stock_daytimes in stock_daytimes_map.values():
		stock_all_daytimes.extend(stock_daytimes)

	    stock_all_daytimes = sorted(stock_all_daytimes, cmp=lambda x,y: cmp(x.day, y.day))        #时间轴顺序

	    allstocks_times_map[symbol] = stock_all_daytimes

	return allstocks_times_map
