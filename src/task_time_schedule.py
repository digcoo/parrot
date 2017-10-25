#coding=utf-8
import time
import traceback
import multiprocessing
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.LogUtils import *
from utils.SinaStockUtils import *
from utils.CommonUtils import *
from dbs.GeodeClient import *
from StockTimeMigrator import *


#定义任务启动函数func
def stock_time_migrator_start(stock_time_migrator):
    stock_time_migrator.start()


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

#当日日期戳
global todaystamp
todaystamp = 0

#每个任务完成的symbols数
num_of_symbol_per_task = 200

#定义本进程的起止位置
stub_start = 0
stub_end = 400

#定义本进程批次号
batch_no = 1

#进程池中最大进程数
process_pool = multiprocessing.Pool(processes=2)


#每日初始化日期
@scheduler.scheduled_job('cron', id='task_new_day_init', hour='9', day_of_week='0-4', max_instances=1)
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
	traceback.print_exc


#股票日交易列表:每个交易日9点同步实时交易数据
@scheduler.scheduled_job('cron', id='stock_time_realtime_spider', minute='*/1', hour='9-23', day_of_week='0-4', max_instances=1)
def stock_time_realtime_spider():
    try:

	if not SinaStockUtils.is_market_open():
	    return

	with_gem = False

	global is_new_day
	if is_new_day:
	    LogUtils.info('=====================init_current_time_data start=============================================')
	    start  = int(time.mktime(datetime.datetime.now().timetuple()))

	    is_new_day = False

	    #更新当前时间戳
	    global todaystamp
	    todaystamp = TimeUtils.get_current_datestamp()

	    #初始化当前股票列表
	    global symbols
	    symbols = GeodeClient.get_instance().query_all_stock_symbols()
	    if not with_gem:
	        symbols = CommonUtils.filter_symbols(symbols)[stub_start : stub_end]

	    #初始化(分时)分析器
	    global stock_time_migrators
	    task_num = int((len(symbols) - 1) / num_of_symbol_per_task) + 1
	    for index in range(task_num):
	        task_symbols = symbols[index * num_of_symbol_per_task : min((index + 1) * num_of_symbol_per_task, len(symbols))]
	        stock_time_migrator = StockTimeMigrator(symbols=task_symbols, todaystamp=todaystamp, identify='time-' + str(batch_no) + '-' + str(index))
	        stock_time_migrators.append(stock_time_migrator)

	    end  = int(time.mktime(datetime.datetime.now().timetuple()))
	    LogUtils.info('init_current_time_data take %s seconds' % (str(end - start), ))
	    LogUtils.info('=====================init_current_time_data end=============================================\n\n\n')

	LogUtils.info('=====================stock_time_realtime_spider start=============================================\n\n\n')
	start  = int(time.mktime(datetime.datetime.now().timetuple()))

	#开启多个进程处理任务
#	task_num = int((len(symbols) - 1) / num_of_symbol_per_task) + 1	
#	pool = multiprocessing.Pool(processes=task_num)

	multiple_results = [process_pool.apply_async(stock_time_migrator_start, (stock_time_migrator, )) for stock_time_migrator in stock_time_migrators]
	[res.get(timeout=120) for res in multiple_results]

#	pool.close()
#	pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束

	end  = int(time.mktime(datetime.datetime.now().timetuple()))
	LogUtils.info('stock_time_realtime_spider take %s seconds' % (str(end - start), ))
	LogUtils.info('=====================stock_time_realtime_spider end=============================================\n\n\n')

    except Exception, e:
	traceback.print_exc()


scheduler.start()

