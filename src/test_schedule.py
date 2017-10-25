#coding=utf-8
import time
import traceback
import sys
from sys import path
path.append('/home/ubuntu/scripts/utils')
from LogUtils import *
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

#是否新的交易日
global is_new_day
is_new_day = True

#总股票symbols
global symbols
symbols = None

#分时轮询器(s)
global stock_time_migrators
stock_time_migrators = []

global todaystamp
todaystamp = 0

#每个任务完成的symbols数
global num_per_task
num_per_task = 500

#每日初始化日期
@scheduler.scheduled_job('cron', id='task_new_day_init', second='*/3', hour='9', day_of_week='0-4', max_instances=1)
def task_new_day_init():

    try:

	LogUtils.info('===============================task_new_day_init start=============================================')
	start  = int(time.mktime(datetime.datetime.now().timetuple()))

	global is_new_day
	is_new_day = True

	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('task_new_day_init take %s seconds' % (str(end - start), ))
	LogUtils.info('===============================task_new_day_init end=============================================\n\n\n')

    except Exception, e:
	traceback.print_exc()


scheduler.start()

