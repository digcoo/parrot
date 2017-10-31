#coding=utf-8
import time
import traceback
import multiprocessing
from utils.TimeUtils import *
from utils.LogUtils import *
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

is_test = True
global todaystamp
todaystamp = 0


#股票日交易列表:每个交易日9点同步实时交易数据
@scheduler.scheduled_job('cron', id='stock_time_realtime_spider', second='*/30', day_of_week='0-4', hour='0-23', max_instances=1)
def stock_time_realtime_spider():
    try:
	global todaystamp
	if TimeUtils.get_current_datestamp() > todaystamp:
	    LogUtils.info('=====================init_current_time_data start=============================================')
	    todaystamp = TimeUtils.get_current_datestamp()

	LogUtils.info('......')

    except Exception, e:
	traceback.print_exc()


scheduler.start()

