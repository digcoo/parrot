#encoding=utf-8
import os
from sys import path
path.append(os.getcwd() + '/vo')
path.append(os.getcwd() + '/utils')
path.append(os.getcwd() + '/quant')
path.append(os.getcwd() + '/dbs')
from bottle import route, run, template, request, response
import pymysql.cursors
import bottle
application = bottle.default_app()
from paste import httpserver
from RedisClient import *
from MysqlClient import *
from SinaStockUtils import *
from StockHitInfo import *
from TimeUtils import *
from BackTest import *
from StockIncubator import *

import jsonpickle
import traceback
import json
import datetime
import time

geode_client = GeodeClient()
redis_client = RedisClient()
mysql_client = MysqlClient()
base_test = BackTest()

stock_day_url = 'http://hq.sinajs.cn/list={0}'

class DateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, datetime.date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj)

@route('/digcoo/recommend', method='GET')
def recommend():
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
	keys = redis_client.keys()
	stock_hits = []
	for key in keys:
	    stock_hits.extend(redis_client.get(key))
	return jsonpickle.encode(convert_json(stock_hits))

#	day_data = redis_client.query_latest_rec('day')
#	day_stocks = convert_json(day_data)
#	time_data = redis_client.query_latest_rec('time')
#	time_stocks = convert_json(time_data)
#	final_stocks = []
#	final_stocks.extend(day_stocks)
#	final_stocks.extend(time_stocks)
#	ret_data = json.dumps(final_stocks)
#	return ret_data
    except Exception, e:
        traceback.print_exc()


@route('/digcoo/hit/add', method='POST')
def hit_add():
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
	symbol = str(request.forms.get('symbol'))
	hit_model = str(request.forms.get('model'))
	status = str(request.forms.get('status'))
	cur_day = TimeUtils.get_current_datestring()
	buy_time = TimeUtils.get_current_timestring()
	stock_day = SinaStockUtils.get_sina_stock_day(symbol)[0]
	stock_hit = StockHitInfo(symbol, stock_day.close + 0.01, hit_model, buy_time, cur_day, status)
	mysql_client.add_stock_hit(stock_hit)
        return '{"code":"200"}'
    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'



@route('/digcoo/hit/getlist', method='GET')
def hit_list():
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
        stub_day = str(request.query.day)
	page = int(request.query.page)
	model = str(request.query.model)
	status = str(request.query.status)
	symbol = str(request.query.symbol)
	size = int(request.query.size)
        retlist = mysql_client.query_stock_hit_page_list(symbol, status, model, page)
	total = mysql_client.query_stock_hit_page_count() * size
	#封装当前价格
	if retlist != None and len(retlist) > 0:
	    retlist = compose_cur_prices(retlist)
	    return '{"total":'  + str(total) + ', "msg":"success", "res":' + json.dumps(retlist, cls=DateEncoder) + '}'
	return '{"total":20, "msg":"success", "res":[]}'
    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'


@route('/digcoo/hit/resistance/<symbol>', method='GET')
def hit_resistance(symbol):
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
        resistance_price = base_test.latest_resistance_price(symbol)
	return '{"code":"200", "resistance":' + str(resistance_price) + '}'
    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'



@route('/digcoo/stock/latestdays/<symbol>', method='GET')
def latest_stock_days(symbol):
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
        latest_stock_days = geode_client.query_stock_days_latest(symbol, 10)
        return '{"code":"200", "latest_days":' + jsonpickle.encode(latest_stock_days) + '}'
    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'

@route('/digcoo/hit/del/<id>', method='GET')
def hit_del(id):
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
	mysql_client.del_stock_hit(id)
	return '{"code":"200"}'
    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'



@route('/digcoo/hit/sell/<id>', method='POST')
def hit_del(id):
    try:
	response.set_header("Access-Control-Allow-Origin", "*")
	symbol = str(request.forms.get('symbol'))
        sell_time = TimeUtils.get_current_timestring()
        stock_day = SinaStockUtils.get_sina_stock_day(symbol)[0]
        mysql_client.sell_stock_hit(id, sell_time, stock_day.close - 0.01)
        return '{"code":"200"}'
    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'



@route('/digcoo/hit/ambush')
def ambush_list():
    try:
        ndays = 35
        response.set_header("Access-Control-Allow-Origin", "*")
        ambush_symbols = []
        for symbol in allstocks_latest_days.keys():
            hist_days = allstocks_latest_days[symbol]
	    if len(hist_days) < 2:
		continue
            for i in range(1, min(ndays, len(hist_days) - 1)):
                if hist_days[i].last_close > 0 and (BaseStockUtils.change_shadow2(hist_days[i]) > 0.05 or hist_days[i].high  > 1.06 * hist_days[i].last_close) and hist_days[0].close < hist_days[i]:
                    ambush_symbols.append({"symbol":symbol})
		    break

	return '{"total":'  + str(1) + ', "msg":"success", "res":' + jsonpickle.encode(ambush_symbols) + '}'

    except Exception, e:
        traceback.print_exc()
    return '{"code":"500"}'


#前期有大涨
@route('/digcoo/hit/incubator')
def incubator_list():
    try:
        response.set_header("Access-Control-Allow-Origin", "*")
	incubator_symbols = []
	stocks_weights = stock_incubator.stocks_weights
	if stocks_weights is not None:
	    for symbol in stocks_weights.keys():
		incubator_symbols.append({'symbol':symbol, 'weight':stocks_weights[symbol]})

	if len(incubator_symbols) > 0:
	    incubator_symbols = sorted(incubator_symbols, key=lambda s_w:s_w['weight'], reverse=True)

	return '{"total":'  + str(1) + ', "msg":"success", "res":' + jsonpickle.encode(incubator_symbols) + '}'

    except Exception, e:
	traceback.print_exc()


def compose_cur_prices(retlist):
    symbols = ''
    if retlist != None and len(retlist) > 0:
	for row in retlist:
	    symbols += row['symbol'] + ','

    stocks_day = SinaStockUtils.get_sina_stock_day(symbols)
    for row in retlist:
	for stock_day in stocks_day:
	    if row['symbol'] == stock_day.symbol:
		row['cur_price'] = stock_day.close
    return retlist


def convert_json(data):
    final_data = []
    if data is not None:
	for cursor in data:
	    item = {'symbol':cursor[0], 'op':cursor[1], 'high':cursor[2], 'low':cursor[3], 'close':cursor[4], 'last_close':cursor[5], 'model':cursor[6]}
	    final_data.append(item)
    return final_data



#缓存历史日交易数据
def cache_hist_days():
    try:
        symbols = geode_client.query_all_stock_symbols()
        stocks_hist_days = {}
        for symbol in symbols:
            if CommonUtils.filter_symbol(symbol) is not None:
                stock_latest_days = geode_client.query_stock_days_latest(symbol, 30)
                stocks_hist_days[symbol] = stock_latest_days

        return stocks_hist_days
    except Exception, e:
        traceback.print_exc()

    return None


#allstocks_latest_days = cache_hist_days()
#stock_incubator = StockIncubator(allstocks_latest_days)


httpserver.serve(application, host='0.0.0.0', port=9090)


print 'cache hist days finished....'
