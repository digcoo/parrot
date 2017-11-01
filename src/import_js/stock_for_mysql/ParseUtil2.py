# encoding=utf8  
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
#import cPickle as pickle

from StockInfo import *
from StockDayInfo import *

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
		if stock_day.vol != '0':
		    stocks_day.append(stock_day)
#		print pickle.dumps(stock)
	return stocks_day

    @staticmethod
    def compose_stock_day_info(line):
	symbol = line[11: line.index('=')]
        line_data = line[line.index('"') + 1 : line.index(';') -1]
        split = line_data.split(',')
        stock = StockDayInfo()
	stock.id = symbol + split[30].strip().replace('-', '')
	stock.symbol = symbol	#代码symbol
        stock.op = float(split[1])   #开盘价
        stock.close = float(split[3])   #当前价
	stock.high = float(split[4])   #最高价
	stock.low = float(split[5])   #最低价
	stock.buy1 = float(split[6])   #买一价
	stock.sell1 = float(split[7])   #卖一价
	stock.vol = float(split[8])   #成交量(股)
	stock.money = float(split[9])   #成交总金额(元)
	stock.buy1_vol = float(split[10])   #买一量(股)
        stock.sell1_vol = float(split[20])   #卖一量(股)
	stock.day = datetime.datetime.strptime(split[30].strip(), "%Y-%m-%d").date()
	return stock

    @staticmethod
    def compose_stock_days(symbol, data):
	stock_days = []
	for index, row in data.iterrows():   # 获取每行的index、row
	    stock_day = StockDayInfo()
	    day = index
	    stock_day.id = symbol + day
            stock_day.symbol = symbol   #代码symbol
            stock_day.op = row['open']   #开盘价
            stock_day.close = row['close']   #当前价
            stock_day.high = row['high']   #最高价
            stock_day.low = row['low']   #最低价
#           stock_day.buy1 = row['']   #买一价
#           stock_day.sell1 = row['']   #卖一价
            stock_day.vol = row['volume']   #成交量(股)
#            stock_day.money = row['money']   #成交总金额(元)
#           stock_day.buy1_vol = split[10]   #买一量(股)
#           stock_day.sell1_vol = split[20]   #卖一量(股)
	    stock_day.day = index + ' 15:00:00'
 	    stock_days.append(stock_day)
        return stock_days

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
	    stock_day.day = datetime.datetime.strptime(tds[0].get_text().strip(), "%Y-%m-%d").date()
	    stock_day.op = float(tds[1].get_text().strip())
	    stock_day.high = float(tds[2].get_text().strip())
	    stock_day.close = float(tds[3].get_text().strip())
	    stock_day.low = float(tds[4].get_text().strip())
	    stock_day.vol = float(tds[5].get_text().strip())
	    stock_day.money = float(tds[6].get_text().strip())
	    stock_day.symbol = symbol
	    stock_day.id = symbol + tds[0].get_text().strip().repace('-', '')
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
    def parse_stock_list(content):
	return ''
