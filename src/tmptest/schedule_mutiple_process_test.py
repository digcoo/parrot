import multiprocessing
import traceback
from Task import *
from apscheduler.schedulers.blocking import BlockingScheduler


def start(task):
    task.start()


scheduler = BlockingScheduler()


is_test = True


pool = multiprocessing.Pool(processes=2)

@scheduler.scheduled_job('cron', id='task_new_day_init', second='*/3', day_of_week='0-4', max_instances=1)
def test():

    try:
	if is_test:
	    print 'is_test'
	tasks = [Task('task1'), Task('task2'), Task('task3')]
	multiple_results = [pool.apply_async(start, (task, )) for task in tasks]
	print([res.get(timeout=100) for res in multiple_results])

#	pool.join()

    except Exception, e:
	traceback.print_exc()

scheduler.start()
