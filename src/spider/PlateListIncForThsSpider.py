#encoding=utf8  

import time
import urllib2
import demjson as json
import traceback
from utils.HttpUtils import *
from utils.ObjectUtils import *
from utils.ParseForThsUtils import *
from dbs.GeodeClient import *
from vo.PlateInfo import *
from dbs.MysqlClient import *

'''
同花顺板块：概念、地域、行业  + 板块下股票列表
'''
class PlateListIncForThsSpider:

    def __init__(self):
	self.plate_list_url = 'http://q.10jqka.com.cn/{0}/'
	self.rel_gn_plate_stock_list_url = 'http://q.10jqka.com.cn/{0}/detail/order/desc/page/{1}/ajax/1/code/{2}'
	self.rel_other_plate_stock_list_url = 'http://q.10jqka.com.cn/{0}/detail/field/199112/order/desc/page/{1}/ajax/1/code/{2}'
	self.plate_detail_url = 'http://q.10jqka.com.cn/{0}/detail/code/{1}/'


#///////////////////////////////plate_list/////////////////////////////////////////////////////////////////////////////////////////////////

    def get_plate_list(self):
	try:
	    all_plates = []
	
	    dy_plates = self.get_plate_list_from_category('dy')
	    LogUtils.info('get_plate_list_for_dy, plates_size = ' + str(len(dy_plates)))
	
	    thshy_plates = self.get_plate_list_from_category('thshy')
	    LogUtils.info('get_plate_list_for_thshy, plates_size = ' + str(len(thshy_plates)))

	    gn_plates = self.get_plate_list_from_category('gn')
	    LogUtils.info('get_plate_list_for_gn, plates_size = ' + str(len(gn_plates)))

	    all_plates.extend(dy_plates)
#	    all_plates.extend(thshy_plates)
#	    all_plates.extend(gn_plates)

	    return all_plates
	except Exception, e:
            traceback.print_exc()
	return None

    def get_plate_list_from_category(self, category):
	try:
            url = self.plate_list_url.format(category)
#	    LogUtils.info('get_plate_list_from_category, url = ' + url)
            content = self.get_html(url)
	    plates = ParseForThsUtils.compose2_plates_from_ths(content, category)

#	    LogUtils.info('get_plate_list_from_category, category = ' + category + ', plates = ' + jsonpickle.encode(plates))

#	    plates = self.get_plate_symbols(plates)

	    #save
	    GeodeClient.get_instance().add_batch_plates(plates)

	    return plates
	except Exception, e:
	    traceback.print_exc()
	    LogUtils.info('get_plate_list_from_category exception..., url = ' + url)
	return None


    def get_plate_list_from_plates(self, plates):
        try:

            plates = self.get_plate_symbols(plates)

            #save
            MysqlClient.get_instance().add_batch_plates(plates)

            return plates
        except Exception, e:
            traceback.print_exc()
        return None


    def get_plate_symbols(self, plates):
	if plates is not None:
	    for plate in plates:
		url = self.plate_detail_url.format(plate.category, plate.id)
		LogUtils.info('get_plate_symbols, url = ' + url)
		content = self.get_html(url)
		symbol = ParseForThsUtils.parse_plate_symbol(content)
		plate.symbol = symbol
		MysqlClient.get_instance().add_batch_plates([plate])
	return plates

#///////////////////////////////plate_list/////////////////////////////////////////////////////////////////////////////////////////////////
		
#///////////////////////////////rel_plate_stock/////////////////////////////////////////////////////////////////////////////////////////////////

    def get_all_plate_stocks(self, plates):
	for plate in plates:
	    rel_plate_stocks = self.get_plate_stocks(plate)
	    MysqlClient.get_instance().add_batch_rel_plate_stocks(rel_plate_stocks)
	    LogUtils.info('get_rel_plate_stock, code[id] = %s, symbol = %s, name = %s, category = %s, rel_size = %s' % (plate.id, plate.symbol, plate.name, plate.category, len(rel_plate_stocks)))
	    time.sleep(1)

    def get_plate_stocks(self, plate):
	rel_plate_stocks = []
	page = 1
	try:

            url = self.get_plate_stock_url(plate.id, plate.category, page)
            content = self.get_html(url)
            plate_stocks = ParseForThsUtils.parse_plate_stocks(plate, content)
            while plate_stocks is not None and len(plate_stocks) > 0:
		rel_plate_stocks.extend(plate_stocks)
            
                page += 1
                url = self.get_plate_stock_url(plate.id, plate.category, page)
                content = self.get_html(url)
                plate_stocks = ParseForThsUtils.parse_plate_stocks(plate, content)

	except Exception, e:
	    traceback.print_exc()
	    LogUtils.info('rel_plate_stock exception... url = '+ rel_plate_stock_req_url)
	return rel_plate_stocks

    def get_plate_stock_url(self, plate_code, category, page):
	if category == 'gn':
	    return self.rel_gn_plate_stock_list_url.format(category, page, plate_code)
	else:
	    return self.rel_other_plate_stock_list_url.format(category, page, plate_code)

#///////////////////////////////rel_plate_stock/////////////////////////////////////////////////////////////////////////////////////////////////


    def get_html(self, url):
        try:
            headers = {}
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


    def get_html_with_single(self, url):

	response = None
        try:
	    response = urllib2.urlopen(url)
	    buf = response.read()
	    try:
		return buf.decode("gbk")
	    except Exception, e:
		traceback.print_exc()
        except Exception, e:
            traceback.print_exc()
	    return None
	finally:
	    if response is not None:
		response.close()

if __name__ == '__main__':
    spider = PlateListIncForThsSpider()
    all_plates = spider.get_plate_list()
#    all_plates_dic = MysqlClient.get_instance().query_plates_by_ids(['301402', '302045', '300075'])
#    all_plates = ObjectUtils.dic_2_object(all_plates_dic)
#    all_plates = spider.get_plate_list_from_plates(all_plates)

#    all_plates_dic = MysqlClient.get_instance().query_plates_by_ids(['300451','301715','301455','305794','301100','302034','300127','300843'])
#    all_plates = ObjectUtils.dic_2_object(all_plates_dic)
#    print jsonpickle.encode(all_plates)
#    spider.get_all_plate_stocks(all_plates)

