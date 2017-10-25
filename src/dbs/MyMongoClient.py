#encoding=utf-8
import pymongo
import jsonpickle

class MyMongoClient:

    __instance = None

    @staticmethod
    def get_instance():
	if MyMongoClient.__instance == None:
	    MyMongoClient.__instance = MyMongoClient()
	return MyMongoClient.__instance

    def __init__(self):
	self.conn = pymongo.MongoClient('172.31.11.83', 27017)

    def add_stock_times(self, symbol, stock_times):
	stock_time_db_repo = self.conn['stock-min-final']
	for stock_time in stock_times:
	    stock_time._id = stock_time.id
	    stock_time_db_repo[symbol].save(eval(jsonpickle.encode(stock_time)))

    def create_index(self, symbol):
	stock_time_db_repo = self.conn['stock-min-final']
	stock_time_db_repo[symbol].create_index([('day', pymongo.ASCENDING)])	#按时间增序建立索引


if __name__ == '__main__':

    client = MyMongoClient.get_instance()
    client.create_index('sh601111')
#    client.add_stock_times('symbol_test', [{'_id':'20170120', 'op' : 12.2, 'close':23.1}])

#    print db_client.collection_names()
