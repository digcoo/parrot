#encoding=utf-8

import traceback
from utils.LogUtils import *
from utils.ParseUtil import *
from utils.SinaStockUtils import *
from dbs.GeodeClient import *


class DataContainer:

    def __init__(self, symbols):
        self.hist_times = None
        self.hist_days = None
        self.hist_weeks = None
        self.hist_months = None
	self.suspend_symbols = []                #今日停盘的票
	self.market_symbols = []                 #正常交易的票
	self.re_market_symbols = []              #今日复盘的票
	try:

            self.hist_times = self.cache_hist_times(symbols)
            self.hist_days = self.cache_hist_days(symbols)
            self.hist_weeks = self.cache_hist_weeks(symbols)
            self.hist_months = self.cache_hist_months(symbols)
	    self.suspend_symbols, self.market_symbols, self.re_market_symbols = self.cache_market_stocks(symbols)

	except Exception, e:
	    traceback.print_exc()


    #缓存历史日交易数据
    def cache_hist_days(self, symbols):
        allstocks_latest_days = {}
        LogUtils.info('StockTimeAnalyzer cache_hist_days ......')
        for symbol in symbols:
            stock_latest_days = GeodeClient.get_instance().query_stock_days_latest(symbol, 70)
            allstocks_latest_days[symbol] = stock_latest_days

        return allstocks_latest_days

    #缓存历史周交易数据
    def cache_hist_weeks(self, symbols):
        allstocks_latest_weeks = {}
        LogUtils.info('StockTimeAnalyzer cache_hist_weeks ......')
        for symbol in symbols:
            stock_latest_weeks = GeodeClient.get_instance().query_stock_weeks_latest(symbol, 70)
            allstocks_latest_weeks[symbol] = stock_latest_weeks

        return allstocks_latest_weeks


    #缓存历史周交易数据
    def cache_hist_months(self, symbols):
        allstocks_latest_months = {}
        LogUtils.info('StockTimeAnalyzer cache_hist_months ......')
        for symbol in symbols:
            stock_latest_months = GeodeClient.get_instance().query_stock_months_latest(symbol, 70)
            allstocks_latest_months[symbol] = stock_latest_months

        return allstocks_latest_months


    #缓存历史日分时交易数据
    def cache_hist_times(self, symbols):
        allstocks_latest_times = {}
        LogUtils.info('StockTimeAnalyzer cache_hist_times ......')

        size = 50
        page = 1
        start = (page - 1) * size
        end = page * size if page * size < len(symbols) else len(symbols)
        temp_symbols = symbols[start : end]
        while(len(temp_symbols) > 0):
            stock_times = GeodeClient.get_instance().query_stock_time_trades_map_by_idlist(temp_symbols)
            allstocks_latest_times.update(stock_times)

            page += 1
            start = (page - 1) * size
            end = page * size if page * size < len(symbols) else len(symbols)
            temp_symbols = symbols[start : end]

        allstocks_latest_times = ParseUtil.compose_stock_times_from_daytimes_map(allstocks_latest_times)

        return allstocks_latest_times


    #初始化今日开盘情况
    def cache_market_stocks(self, symbols):
	#获取股票数据
	all_stocks = GeodeClient.get_instance().query_stocks_by_ids(symbols)
	
	#获取当日开盘数据
	current_stocks_day = SinaStockUtils.get_current_stock_days(symbols)
	(suspend_stocks, market_stocks, re_market_stocks) = ParseUtil.compose_stocks_market(all_stocks, current_stocks_day)
	return self.compose_symbols(suspend_stocks, market_stocks, re_market_stocks)

    def compose_symbols(self, suspend_stocks, market_stocks, re_market_stocks):
        suspend_symbols = []
        market_symbols = []
        re_market_symbols = []
        for stock in suspend_stocks:
            suspend_symbols.append(stock.id)

        for stock in market_stocks:
            market_symbols.append(stock.id)

        for stock in re_market_stocks:
            re_market_symbols.append(stock.id)
        return suspend_symbols, market_symbols, re_market_symbols
