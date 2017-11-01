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

class ParseForEMUtils:


#///////////////////////////////////////////stock for EM///////////////////////////////////////////////////////////


    @staticmethod
    def parse_realtime_time_stock_trades(json_data, stock):
        if json_data is None or len(json_data.strip()) == 0:
            return None, None, None

	json_obj = jsonpickle.decode(json_data)
	if json_obj.get('data') is None:
	    return None, None, None

        time_trades = []
	info_obj = json_obj['info']
	trade_times = json_obj['data']
        day_str = info_obj['time'][:10].replace('-', '')
        last_close = info_obj['yc']
	total_vol = info_obj['v']

	print 'total_vol = ' + str(total_vol)

        for line in trade_times:
            stock_time = StockTimeInfo()

	    split = line.split(',')
	    min_str = split[0].strip().replace(' ', '').replace(':', '').replace('-', '')
            close = float(split[1])
            vol = float(split[2])
	    avg = float(split[3])
            stock_time.id = stock.id + min_str
            stock_time.day = TimeUtils.datestring2datestamp(min_str, TimeUtils.TIME_FORMAT_YYYYMMDDHHMM)
            stock_time.close = close
	    stock_time.vol = vol
            stock_time.avg = avg
            stock_time.symbol = stock.id
            time_trades.append(stock_time)
	if total_vol != '-':
	    date_stamp = TimeUtils.datestring2datestamp(str(day_str), TimeUtils.DATE_FORMAT_YYYYMMDD)
	    return date_stamp, time_trades, last_close
        return None, None, None


