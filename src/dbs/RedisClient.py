# encoding=utf8
import redis
import json
import jsonpickle
from utils.TimeUtils import *

class RedisClient:

    __instance = None

    @staticmethod
    def get_instance():
        if RedisClient.__instance is None:
            RedisClient.__instance = RedisClient()
        return RedisClient.__instance


    def __init__(self):
        self.client = redis.Redis(host = '127.0.0.1', port = '6379')
	self.key_day = 'day'			
	self.key_time = 'time'			#分时推荐map-time:key

    def keys(self):
	return self.client.keys()

    def put_all_today(self, stocks):
	key = TimeUtils.get_current_datestamp()
	self.client.set(str(key), stocks)

    '''	分时线/日K线推荐  '''
    def put_today_rec(self, stocks, type):
	key = TimeUtils.get_current_datestamp()
	local_rec_stocks_str = self.client.get(str(key))
	local_rec_stocks_map = eval(local_rec_stocks_str) if local_rec_stocks_str is not None else None
	if local_rec_stocks_map is None:
	    local_rec_stocks_map = {}
	
	if type == 'day':
	    local_rec_stocks_map[self.key_day] = stocks
	elif type == 'time':
	    local_rec_stocks_map[self.key_time] = stocks

	self.client.set(str(key), local_rec_stocks_map)

    def put_stock_today(self, stock):
	final_stocks = None
	current_set = self.query_today()
	is_exist = False
	if current_set is not None:
	    final_stocks = eval(current_set)
	    for cursor in final_stocks:
		if cursor[0] == stock[0]:
		    is_exist = True
		    break
	else:
	    final_stocks = []
	if not is_exist:
	    final_stocks.append(stock)
	    self.put_all(final_stocks)

    def query_today(self):
	key = TimeUtils.get_current_datestamp()
	return self.client.get(str(key))

    def query_latest(self):
	latest_day = self.filter_latest_day()
	if latest_day > 0:
	    return self.client.get(str(latest_day))
	return None

    def query_latest_rec(self, type = None):
	latest_day = self.filter_latest_day()
	latest_rec_stocks_str = self.client.get(str(latest_day))
	if latest_rec_stocks_str is not None and len(latest_rec_stocks_str) > 0:
	    latest_rec_stocks_map = eval(latest_rec_stocks_str)
	    if type == 'day':
		return latest_rec_stocks_map.get(self.key_day)
	    elif type == 'time':
		return latest_rec_stocks_map.get(self.key_time)
	    else:
		return latest_rec_stocks_map
	return None

    def filter_latest_day(self):
	days = self.keys()
	latest_day = 0
	if days is not None:
	    for day in days:
		if day > latest_day:
		    latest_day = day
	return latest_day
if __name__ == '__main__':
    stock = ('test', '13.30', 'ModelT')
    redis_client = RedisClient()
    #redis_client.put_stock_today(stock)
#    all_d = redis_client.query_today()
#    all_keys= redis_client.keys()
    print redis_client.query_latest_rec(type=None)

