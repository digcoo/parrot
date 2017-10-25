#encoding=utf-8
import sys
sys.path.append("..")

from utils import *
from quant import *
from vo import *
from dbs import *
from gemfire import *

import jsonpickle as json

from GeodeClient import *
from CloseTest import *
from TimeTest import *

class BackExportTest:

    def __init__(self):
	self.geode_client = GeodeClient.get_instance()
	self.redis_client = RedisClient.get_instance()
	self.symbols = self.geode_client.query_all_stock_symbols()
	self.test_days = 1


    def test_hit_for_close(self):
	for symbol in self.symbols:
	    hist_days = self.geode_client.query_stock_days_latest(symbol, 300)
	    test_close = CloseTest(hist_days, symbol, self.test_days)
	    test_close.test()
	    break


    def test_hit_for_time(self):
	all_hit_lines_map = {}			#{model[str], lines_data[list]}
	for symbol in self.symbols:
	    hist_days = self.geode_client.query_stock_days_latest(symbol, 20)
	    hist_times_map = self.geode_client.query_stock_time_trades_map_by_idlist([symbol])
	    if hist_times_map is not None and len(hist_times_map) > 0:
		hist_times_map = hist_times_map.get(symbol)
	    test_time = TimeTest(hist_days, hist_times_map, symbol, self.test_days)
            model, lines_data = test_time.test()
	    if lines_data is not None and len(lines_data) > 0:
		if all_hit_lines_map.get(model) is None:
		    all_hit_lines_map[model] = lines_data
		else:
		    all_hit_lines_map.get(model).extend(lines_data)
	FileUtils.output_lines_data(all_hit_lines_map.values()[0], all_hit_lines_map.keys()[0], 'all_symbols')

if __name__ == '__main__':
    base_test = BackExportTest()
#    base_test.test_hit_for_close()
    base_test.test_hit_for_time()

