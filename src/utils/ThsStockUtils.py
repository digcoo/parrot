#encoding=utf-8
import traceback
import urllib2
import traceback
import jsonpickle

from utils.ParseUtil import *
from utils.ParseForThsUtils import *
from utils.HttpUtils import *


class ThsStockUtils:
    
    stock_timely_realtime_url = 'http://d.10jqka.com.cn/v6/time/hs_{0}/today.js'               #code
    stock_detail_url = 'http://stockpage.10jqka.com.cn/{0}/'                   #code(stock.id[2:])

    @staticmethod
    def get_realtime_time_stock_trades(symbol):
	url = None
	content = None
	try:
            stock = StockInfo()
            stock.id = symbol
            url = ThsStockUtils.stock_timely_realtime_url.format(stock.id[2:])
            content = ThsStockUtils.get_html(url, stock)
            date_stamp, stock_realtime_time_trades, last_close = ParseForThsUtils.parse_realtime_time_stock_trades(content, stock)
            return date_stamp, stock_realtime_time_trades, last_close	    
	except Exception, e:
	    traceback.print_exc()
        return None, None, None

    @staticmethod
    def get_html(url, stock):
        try:
            headers = {}
            headers['Referer'] = ThsStockUtils.stock_detail_url.format(stock.id[2:])
	    headers['Cookie'] = 'v=AXbsO22yMyTISMfA5Mnezwitx6d9l7rRDNvuNeBfYtn0IxgTSCcK4dxrPkCw'
            ntries = 100
            loop = 0
            while loop < ntries:
                loop += 1
                content = HttpUtils.get(url, headers, 'gbk')
                if content is not None:
                    return content

                LogUtils.info('html get content exception, now retry %s times' % (loop, ))

                time.sleep(5)              #wait5s
        except Exception, e:
            traceback.print_exc()

        return None


if __name__ == '__main__':
    print jsonpickle.encode(ThsStockUtils.get_realtime_time_stock_trades('sh601555'))
