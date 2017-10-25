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
同花顺实时交易
'''
class PlateDayIncForThsSpider:

    def __init__(self):
        self.plate_timely_realtime_url = 'http://d.10jqka.com.cn/v4/time/bk_{0}/today.js'
        self.plate_daily_realtime_url = 'http://d.10jqka.com.cn/v4/line/bk_{0}/01/today.js'             #symbol
        self.plate_weekly_realtime_url = 'http://d.10jqka.com.cn/v4/line/bk_{0}/11/today.js'             #symbol
        self.plate_monthly_realtime_url = 'http://d.10jqka.com.cn/v4/line/bk_{0}/21/today.js'   #symbol
        self.plate_detail_url = 'http://q.10jqka.com.cn/{0}/detail/code/{1}/'                   #code(palte.id)



    def get_all_plates_realtime_trades(self):
        all_plates = MysqlClient.get_instance().query_all_plates()
        all_plates = ObjectUtils.dic_2_object(all_plates)

	plates_day = []
	plates_week = []
	plates_month = []

	fail_plates = []

        for plate in all_plates:
	    try:
#		LogUtils.info('=================================plate_day_inc_for_ths on, symbol=%s, code=%s======================================================\n' % (plate.symbol, plate.id, ))
#		plate_realtime_time_trades, last_close = self.get_realtime_time_plate_trades(plate)
#		LogUtils.info('get_realtime_time_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id + ', trades_size = ' + str(len(plate_realtime_time_trades))+ '\n')

		plate_realtime_day_trades = self.get_realtime_day_plate_trades(plate)
		if plate_realtime_day_trades is None:
		    fail_plates.append(plate)
		    continue
#  		plate_realtime_day_trades.last_close = last_close
		plates_day.append(plate_realtime_day_trades)
#		LogUtils.info('get_realtime_day_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id + ', trades_size = ' + str(len(plate_realtime_day_trades)) + '\n')
#		LogUtils.info('get_realtime_day_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id + ', trades = ' + jsonpickle.encode(plate_realtime_day_trades)+'\n')
		
		plate_realtime_week_trades = self.get_realtime_week_plate_trades(plate)
		if plate_realtime_week_trades is None:
		    fail_plates.append(plate)
		    continue
		plates_week.append(plate_realtime_week_trades)
#		LogUtils.info('get_realtime_week_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id + ', trades_size = ' + str(len(plate_realtime_week_trades)) + '\n')
#		LogUtils.info('get_realtime_week_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id + ', trades = ' +jsonpickle.encode(plate_realtime_week_trades)+'\n')
		
		plate_realtime_month_trades = self.get_realtime_month_plate_trades(plate)
		if plate_realtime_month_trades is None:
		    fail_plates.append(plate)
		    continue
		plates_month.append(plate_realtime_month_trades)
#		LogUtils.info('get_realtime_month_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id + ', trades_size = ' + str(len(plate_realtime_month_trades))+'\n')
#		LogUtils.info('get_realtime_month_plate_trades, symbol = ' + plate.symbol + ', code = ' + plate.id +', trades = '+jsonpickle.encode(plate_realtime_month_trades)+'\n')
	    except Exception, e:
		traceback.print_exc()
		fail_plates.append(plate)
	GeodeClient.get_instance().add_batch_plate_days(plates_day)
	GeodeClient.get_instance().add_batch_plate_weeks(plates_week)
	GeodeClient.get_instance().add_batch_plate_months(plates_month)
	LogUtils.info('plate_day_inc_for_ths_spider fail_plates : ' + jsonpickle.encode(fail_plates) + ', fail_plates_size = ' + str(len(fail_plates)) + '\n')

    def get_realtime_time_plate_trades(self, plate):
        url = self.plate_timely_realtime_url.format(plate.symbol)
        content = self.get_html(url, plate)
        plate_realtime_time_trades, last_close = ParseForThsUtils.parse_realtime_time_plate_trades(content, plate)
#	LogUtils.info('get_realtime_time_plate_trades, symbol = ' + plate.symbol + ', trades = ' + jsonpickle.encode(plate_realtime_time_trades)+ '\n')
	return plate_realtime_time_trades, last_close
	


    def get_realtime_day_plate_trades(self, plate):
        url = self.plate_daily_realtime_url.format(plate.symbol)
        content = self.get_html(url, plate)
        plate_realtime_day_trades = ParseForThsUtils.parse_realtime_line_plate_trades(content, plate, 'day')
        return plate_realtime_day_trades



    def get_realtime_week_plate_trades(self, plate):
        url = self.plate_weekly_realtime_url.format(plate.symbol)
        content = self.get_html(url, plate)
        plate_realtime_week_trades = ParseForThsUtils.parse_realtime_line_plate_trades(content, plate, 'week')
        return plate_realtime_week_trades


    def get_realtime_month_plate_trades(self, plate):
        url = self.plate_monthly_realtime_url.format(plate.symbol)
        content = self.get_html(url, plate)
        plate_realtime_month_trades = ParseForThsUtils.parse_realtime_line_plate_trades(content, plate, 'month')
        return plate_realtime_month_trades


    def get_html(self, url, plate):
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
    spider = PlateDayIncForThsSpider()
    spider.get_all_plates_realtime_trades()

