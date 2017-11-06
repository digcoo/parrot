# encoding=utf8  
import jsonpickle
import time
import datetime
import traceback
import json
from vo.StockTimeInfo import *
from vo.BusinessInfo import *
from vo.BusinessDayInfo import *
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


#///////////////////////////////////////////stock for EM///////////////////////////////////////////////////////////



#///////////////////////////////////////////business for EM///////////////////////////////////////////////////////////

    @staticmethod
    def parse_business_list(json_data):
	try:
	    if json_data is not None and len(json_data) > 0:
		json_list = jsonpickle.decode(json_data).get('data')
		business_list = []
		for json_obj in json_list:
		    business_info = BusinessInfo()
		    business_info.id = json_obj.get('SalesCode')
		    business_info.name = json_obj.get('SalesName')
		    business_list.append(business_info)
		return business_list if len(business_list) > 0 else None
	except Exception, e:
	    traceback.print_exc()
	return None


#///////////////////////////////////////////business for EM///////////////////////////////////////////////////////////


#///////////////////////////////////////////business-day for EM///////////////////////////////////////////////////////////



#///////////////////////////////////////////business-day for EM///////////////////////////////////////////////////////////

    @staticmethod
    def parse_business_days(json_data):
        try:
            if json_data is not None and len(json_data) > 0:
                json_list = jsonpickle.decode(json_data).get('data')
                business_days = []
                for json_obj in json_list:
                    business_day = BusinessDayInfo()
                    business_day.b_symbol = json_obj.get('SalesCode')
                    business_day.b_name = json_obj.get('SalesName')
		    business_day.s_symbol = 'sh' + json_obj.get('SCode') if json_obj.get('SCode').startswith('6') else 'sz' + json_obj.get('SCode')
		    business_day.s_name = json_obj.get('SName')
		    business_day.day = json_obj.get('TDate')
		    business_day.sell_money = float(json_obj.get('ActSellNum')) if len(json_obj.get('ActSellNum')) > 2 else 0.0
		    business_day.buy_money = float(json_obj.get('ActBuyNum')) if len(json_obj.get('ActBuyNum')) > 2 else 0.0
		    business_day.id = business_day.b_symbol + business_day.s_symbol + json_obj.get('TDate').replace('-', '')
                    business_days.append(business_day)
                return business_days if len(business_days) > 0 else None
        except Exception, e:
            traceback.print_exc()
        return None
