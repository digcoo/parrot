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
营业部日交易列表
'''
class BusinessDayIncSpider:

    def __init__(self):
	self.business_day_url = 'http://data.eastmoney.com/DataCenter_V3/stock2016/jymx.ashx?pagesize={0}&page={1}&param=&sortRule=-1&sortType=&gpfw=0&code={2}'


#///////////////////////////////business_day/////////////////////////////////////////////////////////////////////////////////////////////////

    #爬取营业部最近的交易记录
    def get_latest_business_days(self, symbols):
        try:
            for symbol in symbols:

                self.get_single_business_latest_day(symbol)

        except Exception, e:
            traceback.print_exc()
        return None



    def get_single_business_latest_day(self, symbol):
        try:

            page_size = 50
            page = 1
            url = self.business_day_url.format(page_size, page, symbol)
            content = EMStockUtils.get_html(url)
            business_days = ParseForEMUtils.parse_business_days(content)
            if (business_days is not None and len(business_days) > 0):
                MysqlClient.get_instance().add_batch_business_days(business_days)

        except Exception, e:
            traceback.print_exc()
        return None



    #爬去营业部所有的历史交易记录
    def get_all_business_days(self, symbols):
	try:
	    for symbol in symbols:

		business_days = self.get_single_business_days(symbol)

	except Exception, e:
            traceback.print_exc()
	return None


    def get_single_business_days(self, symbol):
	try:

            all_business_days = []
            page_size = 50
            page = 1
            url = self.business_day_url.format(page_size, page, symbol)
            content = EMStockUtils.get_html(url)
            business_days = ParseForEMUtils.parse_business_days(content)
            while(business_days is not None and len(business_days) > 0):
                #save
		MysqlClient.get_instance().add_batch_business_days(business_days)
#                all_business_days.extend(business_days)
                print symbol + ' business days ' + str(page) + ':' + str(len(business_days))

                page += 1
                url = self.business_day_url.format(page_size, page, symbol)
                content = EMStockUtils.get_html(url)
                business_days = ParseForEMUtils.parse_business_days(content)

		time.sleep(2)

            return all_business_days

	except Exception, e:
	    traceback.print_exc()
	return None

		
#///////////////////////////////business_day/////////////////////////////////////////////////////////////////////////////////////////////////

