# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/vo')
path.append('/home/ubuntu/scripts/utils')

from StockInfo import *
from GeodeClient import *
from PlateInfo import *
'''
'''
class PlateListIncForSinaSpider:

    def __init__(self):
	self.plate_list_url='http://vip.stock.finance.sina.com.cn/q/view/newFLJK.php?param={0}'
	self.size = 80

    def get_plate_list(self):
	try:
	    count = self.get_plate_list_from_category('industry')
	    count += self.get_plate_list_from_category('area')
	    count += self.get_plate_list_from_category('class')
	    print count
	except Exception, e:
            traceback.print_exc()
	return ''

    def get_plate_list_from_category(self, category):
	count = 0
	try:
            url = self.plate_list_url.format(category)
            content = self.get_html(url)
	    content = content[content.index('{') : content.index('}') + 1]
	    plate_map = json.decode(content)
            if plate_map is not None:
		plates = []
		for symbol in plate_map.keys():
		    if symbol is None or len(symbol.strip(' ')) == 0:
			continue
		    split = plate_map[symbol].split(',')
		    plate = PlateInfo()
		    plate.id = symbol
		    plate.name = split[1].strip(' ')
		    plates.append(plate)
		    count += 1
                    print 'symbol={0}, name={1}'.format(plate.id, plate. name)
	    return count
	except Exception, e:
	    traceback.print_exc()
	return 0

    def get_html(self, url):
        try:
	    response = urllib2.urlopen(url)
	    return response.read().decode("gbk")
        except Exception, e:
            print e
        return ''

if __name__ == '__main__':
    spider = PlateListIncForSinaSpider()
    print spider.get_plate_list()

