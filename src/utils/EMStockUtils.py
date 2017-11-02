#encoding=utf-8
import traceback
import urllib2
import traceback
import jsonpickle

from utils.HttpUtils import *
from utils.ParseForEMUtils import *


class EMStockUtils:
    
    stock_timely_realtime_url = 'http://pdfm2.eastmoney.com/EM_UBG_PDTI_Fast/api/js?id={0}&TYPE=r&js=(x)&rtntype=5&isCR=false'               #code

    @staticmethod
    def get_realtime_time_stock_trades(symbol):
	url = None
	content = None
	try:
            stock = StockInfo()
            stock.id = symbol
	    id = symbol[2:] + '1' if symbol[:2]=='sh' else symbol[2:] + '2'
            url = EMStockUtils.stock_timely_realtime_url.format(id)
            content = EMStockUtils.get_html(url, stock)
            date_stamp, stock_realtime_time_trades, last_close = ParseForEMUtils.parse_realtime_time_stock_trades(content, stock)
            return date_stamp, stock_realtime_time_trades, last_close	    
	except Exception, e:
	    traceback.print_exc()
        return None, None, None

    @staticmethod
    def get_html(url, stock):
        try:
            headers = {}
            ntries = 100
            loop = 0
            while loop < ntries:
                loop += 1
                content = HttpUtils.get(url, headers, 'utf-8')
                if content is not None:
                    return content

                LogUtils.info('html get content exception, now retry %s times' % (loop, ))

                time.sleep(5)              #wait5s
        except Exception, e:
            traceback.print_exc()

        return None


if __name__ == '__main__':
    print jsonpickle.encode(ThsStockUtils.get_realtime_time_stock_trades('sh601555'))
