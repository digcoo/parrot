#encoding=utf-8
import traceback
import urllib2
import traceback

from utils.ParseForSinaUtils import *
from utils.TimeUtils import *


class SinaStockUtils:
    
    sina_stock_day_url='http://hq.sinajs.cn/list={0}'

    @staticmethod
    def get_sina_stock_day(symbol):
	try:
	    url = SinaStockUtils.sina_stock_day_url.format(symbol)
	    content = SinaStockUtils.get_html(url)
	    return ParseForSinaUtils.parse_stock_day(content)
	except Exception, e:
	    traceback.print_exc(e)


    @staticmethod
    def get_current_stock_days(symbols):
	all_stock_days = []
        page = 1
        size = 100
        start = (page -1) * size
        end = page * size if page * size < len(symbols) else len(symbols)
	cursor_symbols = symbols[start : end]
	while len(cursor_symbols) > 0:
	    symbols_str = ParseForSinaUtils.parse_stock_ids(cursor_symbols)
	    stock_days = SinaStockUtils.get_sina_stock_day(symbols_str)
	    if stock_days is not None and len(stock_days) > 0:
		all_stock_days.extend(stock_days)

	    page += 1
	    start = (page -1) * size
	    end = page * size if page * size < len(symbols) else len(symbols)
	    cursor_symbols = symbols[start : end]

	return all_stock_days


    @staticmethod
    def is_market_open():
        try:
            stock_day = SinaStockUtils.get_sina_stock_day('sh000001')
            if stock_day is not None and len(stock_day) > 0 and  stock_day[0].day == TimeUtils.get_current_datestamp():
                return True

        except Exception, e:
            traceback.print_exc()
        return False


    @staticmethod
    def get_html(url):
        try:
            response = urllib2.urlopen(url)
            return response.read().decode("gbk")
        except Exception, e:
	    traceback.print_exc()
        return ''


if __name__ == '__main__':
    print SinaStockUtils.get_sina_stock_day('sh601555')
