# encoding=utf8  

import time
import urllib2
import demjson as json
import traceback

from utils.ObjectUtils import *
from utils.HttpUtils import *
from utils.ParseForThsUtils import *
from dbs.MysqlClient import *
from dbs.GeodeClient import *
from vo.PlateInfo import *
from vo.PlateDayInfo import *
'''
同花顺日交易历史
'''
class PlateDayHistoryForThsSpider:

    def __init__(self):
	self.plate_timely_list_url = 'http://d.10jqka.com.cn/v4/time/bk_{0}/last.js'
	self.plate_daily_list_url = 'http://d.10jqka.com.cn/v4/line/bk_{0}/01/{1}.js'		#symbol, year
	self.plate_weekly_list_url = 'http://d.10jqka.com.cn/v4/line/bk_{0}/11/last.js'		#symbol
	self.plate_monthly_list_url = 'http://d.10jqka.com.cn/v4/line/bk_{0}/21/last.js'	#symbol
	self.plate_detail_url = 'http://q.10jqka.com.cn/{0}/detail/code/{1}/'


    def get_all_plates_histories(self):
	all_plates = MysqlClient.get_instance().query_all_plates()
	all_plates = ObjectUtils.dic_2_object(all_plates)
	
	self.get_all_plates_days(all_plates)
	self.get_all_plates_weeks(all_plates)
	self.get_all_plates_months(all_plates)

    def get_all_plates_days(self, all_plates):
        if all_plates is not None and len(all_plates) > 0:
            for plate in all_plates:
                self.get_plate_days(plate)


    def get_plate_days(self, plate):
        try:
            stub_year = 2017
            url = self.plate_daily_list_url.format(plate.symbol, stub_year)
            print 'get_plate_days, url = ' + url
            content = self.get_html(plate, url)
            plate_days = ParseForThsUtils.parse_plate_days(plate, content)
            while plate_days is not None and len(plate_days) > 0:

                LogUtils.info('collecting plate days symbol = ' + plate.symbol + ', code = ' + plate.id + ', year = ' + str(stub_year) + ', days_size = ' + str(len(plate_days))  + ', url = ' + url)
                
                #save todo
                GeodeClient.get_instance().add_batch_plate_days(plate_days)

                time.sleep(3)
                stub_year -= 1
                url = self.plate_daily_list_url.format(plate.symbol, stub_year)
                content = self.get_html(plate, url)
                plate_days = ParseForThsUtils.parse_plate_days(plate, content)

        except Exception, e:
            traceback.print_exc()
        return None

		

    def get_all_plates_weeks(self, all_plates):
        if all_plates is not None and len(all_plates) > 0:
            for plate in all_plates:
		url = self.plate_weekly_list_url.format(plate.symbol)
		content = self.get_html(plate, url)
		plate_weeks = ParseForThsUtils.parse_plate_days(plate, content)

		
                if plate_weeks is None or len(plate_weeks) == 0:
                    continue


		LogUtils.info('collecting plate weeks symbol = ' + plate.symbol + ', code = ' + plate.id + ', weeks_size = ' + str(len(plate_weeks)) + ', url = ' + url)

		#save weeks
		GeodeClient.get_instance().add_batch_plate_weeks(plate_weeks)


    def get_all_plates_months(self, all_plates):
        if all_plates is not None and len(all_plates) > 0:
            for plate in all_plates:
                url = self.plate_monthly_list_url.format(plate.symbol)
                content = self.get_html(plate, url)
                plate_months = ParseForThsUtils.parse_plate_days(plate, content)
		
		if plate_months is None or len(plate_months) == 0:
		    continue
		
		LogUtils.info('collecting plate months symbol = ' + plate.symbol + ', code = ' + plate.id + ', months_size = ' + str(len(plate_months))  + ', url = ' + url)

                #save months
		GeodeClient.get_instance().add_batch_plate_months(plate_months)


    def get_html(self, plate, url):
        try:
	    headers = {}
	    headers['Referer'] = self.plate_detail_url.format(plate.category, plate.id)
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
    spider = PlateDayHistoryForThsSpider()
    spider.get_all_plates_histories()

