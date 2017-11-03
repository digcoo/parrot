# encoding=utf8
import os
from gemfire.GemfireClient import *
from utils.ParseForSinaUtils import *
from utils.ThsStockUtils import *
import jsonpickle

from sys import path
path.append(os.getcwd() + '/vo')

from utils.SystemConfig import *

from PlateInfo import *
from PlateDayInfo import *
from StockInfo import *
from StockTimeInfo import *
from StockDayInfo import *

class GeodeClient:


    __instance = None

    @staticmethod
    def get_instance():
	if GeodeClient.__instance is None:
	    GeodeClient.__instance = GeodeClient()
	return GeodeClient.__instance

    def __init__(self):
        self.client = GemfireClient(hostname = SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.GEODE_SERVER_IP), port = SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.GEODE_SERVER_PORT))


    def get(self, key, region_name):
        repo = self.client.create_repository(region_name)
        return repo.get_region().get(key)



#================================================stock=====================================================

    def put_all_stocks(self, stocks):
	stock_repo = self.client.create_repository('stock')
	#stock_region = stock_repo.get_region()
	stock_repo.save(stocks if len(stocks) > 1 else stocks[0])

    def query_all_stock_symbols(self):
        stock_repo = self.client.create_repository('stock')
        stock_region = stock_repo.get_region()
	symbols = stock_region.keys()
#        return CommonUtils.filter_symbols(symbols)
	return symbols


    def query_all_stocks(self):
        paras = []
        paras_types = []
        return self.client.my_query("select_all_stocks", paras, paras_types)


    def query_stocks_by_ids(self, ids):
	stocks = []
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(ids) else len(ids)
        temp_ids = ids[start : end]
	ids_str = ParseForSinaUtils.parse_stock_ids(temp_ids)
	temp_stocks = self.get(ids_str, 'stock')
        while(temp_stocks is not None and start < end):
	    if len(temp_ids) > 1:
		stocks.extend(temp_stocks.get('stock'))
	    else:
		stocks.append(temp_stocks)

            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(ids) else len(ids)
            temp_ids = ids[start : end]
	    ids_str = ParseForSinaUtils.parse_stock_ids(temp_ids)
	    temp_stocks = self.get(ids_str, 'stock')

	return stocks	


    def add_batch_stocks(self, stocks):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(stocks) else len(stocks)
        temp_stocks = stocks[start : end]
        while(len(temp_stocks) > 0 and start < end):
            self.put_all_stocks(temp_stocks)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(stocks) else len(stocks)
            temp_stocks = stocks[start : end]


#================================================stock=====================================================




#================================================stock-day=====================================================

    def put_stocks_day(self, stock_days):
	stock_day_repo = self.client.create_repository('stock-day-final')
	stock_day_repo.save(stock_days if len(stock_days) > 1 else stock_days[0])



    def query_stock_days_latest(self, symbol, ndays):
        paras = [symbol, ndays]
        paras_types = ['String', 'int']
        stock_days = self.client.my_query("select_stock_days_latest", paras, paras_types)
        return stock_days


    def add_batch_stock_days(self, stock_days):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(stock_days) else len(stock_days)
        temp_stock_days = stock_days[start : end]
        while(len(temp_stock_days) > 0 and start < end):
            self.put_stocks_day(temp_stock_days)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(stock_days) else len(stock_days)
            temp_stock_days = stock_days[start : end]



#================================================stock-day=====================================================




#================================================stock-week=====================================================


    def put_stock_weeks(self, stock_weeks):
        stock_week_repo = self.client.create_repository('stock-week-final')
        stock_week_repo.save(stock_weeks if len(stock_weeks) > 1 else stock_weeks[0])



    def query_stock_weeks_latest(self, symbol, nweeks):
        paras = [symbol, nweeks]
        paras_types = ['String', 'int']
        stock_weeks = self.client.my_query("select_stock_weeks_latest", paras, paras_types)
        return stock_weeks



    def add_batch_stock_weeks(self, stock_weeks):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(stock_weeks) else len(stock_weeks)
        temp_stock_weeks = stock_weeks[start : end]
        while(len(temp_stock_weeks) > 0 and start < end):
            self.put_stock_weeks(temp_stock_weeks)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(stock_weeks) else len(stock_weeks)
            temp_stock_weeks = stock_weeks[start : end]


#================================================stock-week=====================================================



#================================================stock-month=====================================================


    def put_stock_months(self, stock_months):
        stock_month_repo = self.client.create_repository('stock-month-final')
	stock_month_repo.save(stock_months if len(stock_months) > 1 else stock_months[0])


    def query_stock_months_latest(self, symbol, nmonths):
        paras = [symbol, nmonths]
        paras_types = ['String', 'int']
        stock_months = self.client.my_query("select_stock_months_latest", paras, paras_types)
        return stock_months



    def add_batch_stock_months(self, stock_months):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(stock_months) else len(stock_months)
        temp_stock_months = stock_months[start : end]
        while(len(temp_stock_months) > 0 and start < end):
            self.put_stock_months(temp_stock_months)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(stock_months) else len(stock_months)
            temp_stock_months = stock_months[start : end]


#================================================stock-month=====================================================


#================================================stock-time begin=====================================================


    def query_stock_time_trades_map_by_idlist(self, ids):
	id_str = ParseForSinaUtils.parse_stock_ids(ids)
	final_stocks_time_trades_map = {}
	stocks_time_trades_map = self.get(id_str, 'stock-time-final')
	if stocks_time_trades_map is not None:
	    if len(ids) > 1:
	        stocks_time_trades = stocks_time_trades_map.get('stock-time-final')
	        for stock_time_trades in stocks_time_trades:
		    if stock_time_trades is not None:
			symbol = stock_time_trades.get(stock_time_trades.keys()[0])[0].symbol
		        final_stocks_time_trades_map[symbol] = stock_time_trades
	    else:
		symbol = stocks_time_trades_map.get(stocks_time_trades_map.keys()[0])[0].symbol
		final_stocks_time_trades_map[symbol] = stocks_time_trades_map

	return final_stocks_time_trades_map

    def put_stock_time_trades(self, symbol, day_datestamp, time_trades):
        stock_time_repo = self.client.create_repository('stock-time-final')
	local_time_trades_map = stock_time_repo.get_region().get(symbol)
	today_time_trades_map = {}
	today_time_trades_map[str(day_datestamp)] = time_trades
	com_stock_time_trades_map = ParseForSinaUtils.compose_stock_time_trades_map(local_time_trades_map, today_time_trades_map)
#	print jsonpickle.encode(com_stock_time_trades_map)
	stock_time_repo.get_region().put(symbol, com_stock_time_trades_map)


#================================================stock-time end=====================================================




#================================================plate=====================================================


    def put_all_plates(self, plates):
        plate_repo = self.client.create_repository('plate')
	plate_repo.save(plates if len(plates) > 1 else plates[0])



    def query_all_plate_ids(self):
        stock_repo = self.client.create_repository('plate')
        stock_region = stock_repo.get_region()
        return stock_region.keys()


    def query_all_plates(self):
        stock_repo = self.client.create_repository('plate')
        paras = []
        paras_types = []
        return self.client.my_query("select_all_plates", paras, paras_types)



    def add_batch_plates(self, plates):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(plates) else len(plates)
        temp_plates = plates[start : end]
        while(len(temp_plates) > 0 and start < end):
            self.put_all_plates(temp_plates)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(plates) else len(plates)
            temp_plates = plates[start : end]


#================================================plate=====================================================




#================================================plate-day=====================================================

    def put_plates_day(self, plate_days):
        plate_day_repo = self.client.create_repository('plate-day-final')
	plate_day_repo.save(plate_days if len(plate_days) > 1 else plate_days[0])



    def query_plate_days_latest(self, symbol, ndays):
        paras = [symbol, ndays]
        paras_types = ['String', 'int']
        plate_days = self.client.my_query("select_plate_days_latest", paras, paras_types)
        return plate_days


    def add_batch_plate_days(self, plate_days):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(plate_days) else len(plate_days)
        temp_plate_days = plate_days[start : end]
        while(len(temp_plate_days) > 0 and start < end):
            self.put_plates_day(temp_plate_days)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(plate_days) else len(plate_days)
            temp_plate_days = plate_days[start : end]


#================================================plate-day=====================================================



#================================================plate-week=====================================================


    def put_plates_week(self, plate_weeks):
        plate_week_repo = self.client.create_repository('plate-week-final')
	plate_week_repo.save(plate_weeks if len(plate_weeks) > 1 else plate_weeks[0])



    def query_plate_weeks_latest(self, symbol, nweeks):
        paras = [symbol, nweeks]
        paras_types = ['String', 'int']
        plate_weeks = self.client.my_query("select_plate_weeks_latest", paras, paras_types)
        return plate_weeks


    def add_batch_plate_weeks(self, plate_weeks):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(plate_weeks) else len(plate_weeks)
        temp_plate_weeks = plate_weeks[start : end]
        while(len(temp_plate_weeks) > 0 and start < end):
            self.put_plates_week(temp_plate_weeks)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(plate_weeks) else len(plate_weeks)
            temp_plate_weeks = plate_weeks[start : end]


#================================================plate-week=====================================================

#================================================plate-month=====================================================


    def put_plates_month(self, plate_months):
        plate_month_repo = self.client.create_repository('plate-month-final')
	plate_month_repo.save(plate_months if len(plate_months) > 1 else plate_months[0])


    def query_plate_months_latest(self, symbol, nmonths):
        paras = [symbol, nmonths]
        paras_types = ['String', 'int']
        plate_months = self.client.my_query("select_plate_months_latest", paras, paras_types)
        return plate_months


    def add_batch_plate_months(self, plate_months):
        page = 1
        size = 50
        start = (page -1) * size
        end = page*size if page * size < len(plate_months) else len(plate_months)
        temp_plate_months = plate_months[start : end]
        while(len(temp_plate_months) > 0 and start < end):
            self.put_plates_month(temp_plate_months)
            page += 1
            start = (page -1) * size
            end = page*size if page * size < len(plate_months) else len(plate_months)
            temp_plate_months = plate_months[start : end]


#================================================plate-month=====================================================


    def test_save(self, stocks):
        stock_repo = self.client.create_repository('test')
	stock_repo.save(stocks if len(stocks) > 1 else stocks[0])
#        stock_repo.save(stocks)

    def test_put(self, key, value):
        stock_repo = self.client.create_repository('test')
        stock_repo.get_region().put(key, value)


if __name__ == '__main__':
    geo_client = GeodeClient()
#    print jsonpickle.encode(geo_client.query_all_stock_symbols())
#    stocks = geo_client.query_all_stocks()
#    print len(geo_client.query_all_stock_symbols())
#    print type(geo_client.query_all_stock_symbols())
#    stock_days = geo_client.query_stock_days_latest('sh600111', 10000)
#    geo_client.add_stock_days_page(stock_days)
#    for i in range(len(stock_days) - 1):
#	stock_days[i].last_close = stock_days[i+1].close

#    print json.encode(stock_days)
#    geo_client.add_stock_days_page(stock_days)

#    plates = geo_client.query_all_plates()
#    symbols = []
#    for plate in plates:
#	symbols.append(plate.symbol + '20171009')
#	symbols.append(plate.symbol + '20171010')
#    print jsonpickle.encode(symbols)


    all_symbols = GeodeClient.get_instance().query_all_stock_symbols()[:100]
    stocks = GeodeClient.get_instance().query_stocks_by_ids(all_symbols)
    print len(stocks)

#    all_stock_day_map = {}
#    all_stock_day_map['sh601101'] = stock_day_times_map
#    GeodeClient.get_instance().test_put('sh601101', stock_day_times_map)

#    print jsonpickle.encode(geo_client.query_stock_time_trades_map_by_idlist(['sh601101']))

#    print jsonpickle.encode(geo_client.query_stock_days_latest('sh601011', 100))
