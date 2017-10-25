import multiprocessing
from Task import *

def start(task):
    task.start()

pool = multiprocessing.Pool(processes=2)

if __name__ == '__main__':

    tasks = [Task('task1'), Task('task2'), Task('task3')]

    multiple_results = [pool.apply_async(start, (task, )) for task in tasks]

    print([res.get(timeout=100) for res in multiple_results])

