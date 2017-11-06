#encoding=utf8  

import time
import urllib2
import demjson as json
import traceback
from utils.HttpUtils import *
from utils.ObjectUtils import *
from dbs.MysqlClient import *
from utils.EMStockUtils import *

'''
营业部列表
'''
class BusinessListIncSpider:

    def __init__(self):
	self.business_list_url = 'http://data.eastmoney.com/DataCenter_V3/stock2016/BusinessRanking/pagesize={0},page={1},sortRule=-1,sortType=,startDate={2},endDate={3},gpfw=0,js=.html?'


#///////////////////////////////business_list/////////////////////////////////////////////////////////////////////////////////////////////////

    def get_business_list(self):
	try:
            all_business = []
            end_date = TimeUtils.get_current_datestamp()
            start_date = TimeUtils.date_add(end_date, -90)
            start_datestring = TimeUtils.timestamp2datestring(start_date)
            end_datestring = TimeUtils.timestamp2datestring(end_date)
            page_size = 50
            page = 1
            url = self.business_list_url.format(page_size, page, start_datestring, end_datestring)
            content = EMStockUtils.get_html(url)
            business_list = ParseForEMUtils.parse_business_list(content)
	    while(business_list is not None and len(business_list) > 0):
		#save
		MysqlClient.get_instance().add_batch_business_list(business_list)
		all_business.extend(business_list)
#		print jsonpickle.encode(business_list)
		print 'business_list ' + str(page) + ':' + str(len(business_list))

		page += 1
		url = self.business_list_url.format(page_size, page, start_datestring, end_datestring)
		content = EMStockUtils.get_html(url)
		business_list = ParseForEMUtils.parse_business_list(content)


	    return all_business
	
	except Exception, e:
            traceback.print_exc()
	return None

		
#///////////////////////////////business_list/////////////////////////////////////////////////////////////////////////////////////////////////

