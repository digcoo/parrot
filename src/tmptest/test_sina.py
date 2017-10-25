# encoding=utf8  
import time
import urllib2

class SpiderTest:

    def __init__(self, is_quant):
	self.is_quant = is_quant
	self.stock_single_url = 'http://hq.sinajs.cn/list={0}'
	print is_quant
	self.stock_analyzer = None
	if is_quant == True:
	    print 'is_quant is true'

    def get_stocks_day_single(self, symbols):
        try:
	    url = self.stock_single_url.format(symbols)
	    content = self.get_html(url)
	    return ParseUtil.parse_stock_day(content)
        except Exception, e:
            print e
        return ''

    def get_html(self, url):
        try:
	    response = urllib2.urlopen(url)
	    return response.read().decode("gbk")
        except Exception, e:
            print e
        return ''


    def get_allstocks_day(self):
	try:
	    while(1 > 0):
		stocks_day = self.get_stocks_day_single('sh601006,sh603098')
		if self.is_quant:
		    print 'start analyze .... '

	except Exception, e:
	    print e


spider = SpiderTest(False)
spider.get_allstocks_day()
