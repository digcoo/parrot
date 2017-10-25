# encoding=utf8  
import jsonpickle
import time
import datetime
import traceback
import json
from vo.PlateInfo import *
from vo.PlateDayInfo import *
from vo.RelPlateStockInfo import *
from vo.StockInfo import *
from vo.StockDayInfo import *
from vo.StockTimeInfo import *
from utils.LogUtils import *

from bs4 import BeautifulSoup
import re

class ParseForThsUtils:

    plate_detail_url_regex = 'http://q.10jqka.com.cn/(.*)/detail/code/(.*?)/'

    #同花顺板块
    @staticmethod
    def compose_plates_from_ths(html_data):
	if html_data is None or len(html_data.strip()) == 0:
	    return None
        plates = []
	soup = BeautifulSoup(html_data)
#	print html_data
	cate_groups = soup.find_all('div', class_='cate_group')
#	print len(cate_groups)
	
	if cate_groups is not None:
	    for cate_group in cate_groups:
		target_as = cate_group.find_all('a')
#		print len(target_as)
		
		for target_a in target_as:
		    link = target_a['href']
		    match_obj = re.match(ParseForThsUtils.plate_detail_url_regex, link, re.M|re.I)
		    name = target_a.get_text().strip()
		    plate = PlateInfo()
		    plate.id = match_obj.group(2)
		    plate.name = name
		    plate.category = match_obj.group(1)
#		    LogUtils.info('code = ' + plate.id + ', name = ' + plate.name + ', category = ' + plate.category)
		    plates.append(plate)
		
	return plates


    @staticmethod
    def compose2_plates_from_ths(html_data, category):
        if html_data is None or len(html_data.strip()) == 0:
            return None
        plates = []
        soup = BeautifulSoup(html_data)
	if category == 'gn':
	    data = soup.find(id='gnSection')['value']
	    if data is not None:
#		data_map = eval(data)
		json_obj = json.loads(data)
#		print json_obj.values()
#		data_map = json.dumps(data).decode("unicode-escape")
		
	#	print data_map
		
		for data in json_obj.values():
                    plate = PlateInfo()
                    plate.id = data['cid']
                    plate.name = data['platename']
                    plate.symbol = data['platecode']
                    plate.category = category
                    plates.append(plate)
		
	else:
	    cate_groups = soup.find_all('div', class_='cate_group')
            if cate_groups is not None:
                for cate_group in cate_groups:
                    target_as = cate_group.find_all('a')

                    for target_a in target_as:
                        link = target_a['href']
                        match_obj = re.match(ParseForThsUtils.plate_detail_url_regex, link, re.M|re.I)
                        name = target_a.get_text().strip()
                        plate = PlateInfo()
                        plate.id = match_obj.group(2)
                        plate.name = name
		        plate.symbol = plate.id
                        plate.category = category
                        plates.append(plate)

        return plates


    #同花顺板块下股票列表
    @staticmethod
    def parse_plate_stocks(plate, html_data):
        if html_data is None or len(html_data.strip()) == 0:
            return None

	rel_stocks = []
	soup = BeautifulSoup(html_data)
	trs = soup.find_all('tr')[1:]
	for tr in trs:
	    tds = tr.find_all('td')
	    if len(tds) < 5:
		continue
	    code = tds[1].get_text()
	    name = tds[2].get_text()
	    rel_plate_stock = RelPlateStockInfo()
	    rel_plate_stock.stock_symbol = 'sh' + code if code.startswith('6') else 'sz' + code
	    rel_plate_stock.stock_name = name
	    rel_plate_stock.plate_code = plate.id
	    rel_plate_stock.plate_name = plate.name
	    rel_plate_stock.id = rel_plate_stock.plate_code + rel_plate_stock.stock_symbol
	    rel_stocks.append(rel_plate_stock)
	return rel_stocks

    @staticmethod
    def parse_plate_symbol(html_data):
	soup = BeautifulSoup(html_data)
	return soup.find(id='clid')['value']


    @staticmethod
    def parse_plate_days(plate, html_data):
	if html_data is None or len(html_data.strip()) == 0:
	    return None
	plate_days = []
	content = html_data[html_data.index('{') : html_data.rindex('}') + 1]
	json_obj = jsonpickle.decode(content)
	data_lines = json_obj['data']
	lines = data_lines.split(';')
	for line in lines:
	    plate_day = PlateDayInfo()
	    split = line.split(',')
	    day_str = split[0]
	    op = float(split[1])
	    high = float(split[2])
	    low = float(split[3])
	    close = float(split[4])
	    vol = float(split[5])
	    money = float(split[6])
	    plate_day.id = plate.id + str(day_str)
	    plate_day.day = TimeUtils.datestring2datestamp(day_str, TimeUtils.DATE_FORMAT_YYYYMMDD)
	    plate_day.op = op
	    plate_day.high = high
	    plate_day.low = low
	    plate_day.close = close
	    plate_day.vol = vol
	    plate_day.money = money
	    plate_day.symbol = plate.symbol
	    plate_days.append(plate_day)
	return plate_days

#///////////////////////////////////////////plate for ths///////////////////////////////////////////////////////////

    @staticmethod
    def parse_realtime_time_plate_trades(html_data, plate):
        if html_data is None or len(html_data.strip()) == 0:
            return None
        time_trades = []
        content = html_data[html_data.index('{') : html_data.rindex('}') + 1]
        json_obj = jsonpickle.decode(content)
	trade_obj = json_obj['bk_' + plate.symbol]
	data_lines = trade_obj['data'].split(';')
	day_str = trade_obj['date']
	last_close = float(trade_obj['pre']) if len(trade_obj['pre']) > 0 else None
        for line in data_lines:
            plate_minute = PlateDayInfo()
            split = line.split(',')
            min_str = split[0]
            close = float(split[1])
            money = float(split[2])
            avg = float(split[3])
            vol = float(split[4])
            plate_minute.id = plate.id + str(day_str) + str(min_str)
            plate_minute.day = TimeUtils.datestring2datestamp(str(day_str) + str(min_str), TimeUtils.TIME_FORMAT_YYYYMMDDHHMM)
            plate_minute.close = close
            plate_minute.vol = vol
            plate_minute.money = money
	    plate_minute.avg = avg
            plate_minute.symbol = plate.symbol
            time_trades.append(plate_minute)
        return time_trades, last_close

    @staticmethod
    def parse_realtime_line_plate_trades(html_data, plate, type):
        if html_data is None or len(html_data.strip()) == 0:
            return None
        line_trades = []
        content = html_data[html_data.index('{') : html_data.rindex('}') + 1]
        json_obj = jsonpickle.decode(content)
        trade_obj = json_obj['bk_' + plate.symbol]
        day_str = trade_obj['1']
        op = trade_obj['7']
        high = trade_obj['8']
        low = trade_obj['9']
        close = trade_obj['11']
        vol = trade_obj['13']
        money = trade_obj['19']
        plate_trade = PlateDayInfo()
        plate_trade.op = op
        plate_trade.high = high
        plate_trade.low = low
        plate_trade.close = close
        plate_trade.vol = vol
        plate_trade.money = money
        plate_trade.symbol = plate.symbol
	id_date_str = ''
	if type == 'day':
	    id_date_str = day_str
	elif type == 'week':
	    todaystamp = TimeUtils.datestring2datestamp(day_str, TimeUtils.DATE_FORMAT_YYYYMMDD)
	    week_friday = TimeUtils.current_friday_from_datestamp(todaystamp)
	    id_date_str = TimeUtils.datestamp2datestring(week_friday, TimeUtils.DATE_FORMAT_YYYYMMDD)
	elif type == 'month':
	    todaystamp = TimeUtils.datestring2datestamp(day_str, TimeUtils.DATE_FORMAT_YYYYMMDD)
	    month_lastday = TimeUtils.lastday_of_month_from_datestamp(todaystamp)
	    id_date_str = TimeUtils.datestamp2datestring(month_lastday, TimeUtils.DATE_FORMAT_YYYYMMDD)
	else:
	    return None

	plate_trade.day = TimeUtils.datestring2datestamp(day_str, TimeUtils.DATE_FORMAT_YYYYMMDD)
	plate_trade.id = plate.symbol + id_date_str
	return plate_trade


#///////////////////////////////////////////plate for ths///////////////////////////////////////////////////////////


#///////////////////////////////////////////stock for ths///////////////////////////////////////////////////////////


    @staticmethod
    def parse_realtime_time_stock_trades(html_data, stock):
        if html_data is None or len(html_data.strip()) == 0:
            return None, None, None
        time_trades = []
        content = html_data[html_data.index('{') : html_data.rindex('}') + 1]
        json_obj = jsonpickle.decode(content)
	trade_obj = json_obj['hs_' + stock.id[2:]]
        data_lines = trade_obj['data'].split(';')
        day_str = trade_obj['date']
        last_close = float(trade_obj['pre']) if len(trade_obj['pre']) > 0 else None
	total_vol = 0
        for line in data_lines:
            stock_time = StockTimeInfo()
            split = line.split(',')
	    if len(split) < 5:
		continue
            min_str = split[0]

	    if split[1].strip() == '':
		return None, None, None

            close = float(split[1])
            money = float(split[2])
            avg = float(split[3])
            vol = float(split[4])
            stock_time.id = stock.id + str(day_str) + str(min_str)
            stock_time.day = TimeUtils.datestring2datestamp(str(day_str) + str(min_str), TimeUtils.TIME_FORMAT_YYYYMMDDHHMM)
            stock_time.close = close
	    stock_time.vol = vol
            stock_time.money = money
            stock_time.avg = avg
            stock_time.symbol = stock.id
            time_trades.append(stock_time)
	    total_vol += vol
	if total_vol > 0.1:
	    date_stamp = TimeUtils.datestring2datestamp(str(day_str), TimeUtils.DATE_FORMAT_YYYYMMDD)
	    return date_stamp, time_trades, last_close
        return None, None, None

    @staticmethod
    def parse_realtime_line_stock_trades(html_data, stock, type):
        if html_data is None or len(html_data.strip()) == 0:
            return None
        line_trades = []
        content = html_data[html_data.index('{') : html_data.rindex('}') + 1]
        json_obj = jsonpickle.decode(content)
        trade_obj = json_obj['hs_' + stock.id[2:]]
        day_str = trade_obj['1']
        op = trade_obj['7']
        high = trade_obj['8']
        low = trade_obj['9']
        close = trade_obj['11']
        vol = trade_obj['13']
        money = trade_obj['19']
        stock_trade = StockDayInfo()
        stock_trade.op = op
        stock_trade.high = high
        stock_trade.low = low
        stock_trade.close = close
        stock_trade.vol = vol
        stock_trade.money = money
        stock_trade.symbol = stock.id
	stock_trade.day = TimeUtils.datestring2datestamp(str(day_str), TimeUtils.DATE_FORMAT_YYYYMMDD)

        id_date_str = ''
        if type == 'day':
            id_date_str = day_str
        elif type == 'week':
            todaystamp = TimeUtils.datestring2datestamp(str(day_str), TimeUtils.DATE_FORMAT_YYYYMMDD)
            week_friday = TimeUtils.current_friday_from_datestamp(todaystamp)
            id_date_str = TimeUtils.datestamp2datestring(week_friday, TimeUtils.DATE_FORMAT_YYYYMMDD)
        elif type == 'month':
            todaystamp = TimeUtils.datestring2datestamp(day_str, TimeUtils.DATE_FORMAT_YYYYMMDD)
            month_lastday = TimeUtils.lastday_of_month_from_datestamp(todaystamp)
            id_date_str = TimeUtils.datestamp2datestring(month_lastday, TimeUtils.DATE_FORMAT_YYYYMMDD)
        else:
            return None

        stock_trade.id = stock.id + id_date_str
        return stock_trade


    @staticmethod
    def parse_stock_days(stock, html_data):
        if html_data is None or len(html_data.strip()) == 0:
            return None
        stock_days = []
        content = html_data[html_data.index('{') : html_data.rindex('}') + 1]
        json_obj = jsonpickle.decode(content)
        data_lines = json_obj['data']
        lines = data_lines.split(';')
        for line in lines:
            stock_day = StockDayInfo()
            split = line.split(',')
            day_str = split[0]
            op = float(split[1])
            high = float(split[2])
            low = float(split[3])
            close = float(split[4])
            vol = float(split[5])
            money = float(split[6])
            stock_day.id = stock.id + day_str
            stock_day.day = TimeUtils.datestring2datestamp(day_str, TimeUtils.DATE_FORMAT_YYYYMMDD)
            stock_day.op = op
            stock_day.high = high
            stock_day.low = low
            stock_day.close = close
            stock_day.vol = vol
            stock_day.money = money
            stock_day.symbol = stock.id
            stock_days.append(stock_day)
        return stock_days


#///////////////////////////////////////////stock for ths///////////////////////////////////////////////////////////
