#encoding=utf-8
from vo.StockDayInfo import *
from vo.StockTimeInfo import *
from utils.TimeUtils import *
import time
import jsonpickle
import traceback

class BaseStockUtils:

    #前第N天交易
    @staticmethod
    def pre_stock_day(stock_days, intv, todaystamp):
	#找到索引日
	if stock_days is None or len(stock_days) == 0:
	    return None
	index = BaseStockUtils.index_less_of(stock_days, todaystamp)
	if len(stock_days) >= (index + intv):
	    return stock_days[index + intv-1]
	return None


    #计算上影线(包括上涨或下跌)
    @staticmethod
    def pre_upper_shadow(stock_days, intv, today):
	stock_day = BaseStockUtils.pre_stock_day(stock_days, intv, today)
	if stock_day.close >= stock_day.op:
	    return round((stock_day.high - stock_day.close) / stock_day.close, 5)
	else:
	    return round((stock_day.high - stock_day.op) / stock_day.op, 5)


    #计算下影线(包括上涨或下跌)
    @staticmethod
    def pre_lower_shadow(stock_days, intv, today):
        stock_day = BaseStockUtils.pre_stock_day(stock_days, intv, today)
	if stock_day.close >= stock_day.op:
            return round((stock_day.op - stock_day.low) / stock_day.low, 5)
        else:
            return round((stock_day.close - stock_day.low) / stock_day.low)


    #计算实体(包括上涨或下跌)
    @staticmethod
    def pre_column_shadow(stock_days, intv, today):
	stock_day = BaseStockUtils.pre_stock_day(stock_days, intv, today)
        if stock_day.close >= stock_day.op:
            return round((stock_day.close - stock_day.op) / stock_day.op, 5)
        else:
            return round((stock_day.op - stock_day.close) / stock_day.close, 5)

    #计算涨幅(包括上涨或下跌)
    @staticmethod
    def pre_change_shadow(stock_days, intv, today):
        stock_day = BaseStockUtils.pre_stock_day(stock_days, intv, today)
	last1_stock_day = BaseStockUtils.pre_stock_day(stock_days, intv + 1, today)
        return round((stock_day.close - last1_stock_day.close) / last1_stock_day.close, 5)


    #前第N天是否红色实体
    @staticmethod
    def pre_is_red(stock_days, intv, today):
        lastN_stock_day = BaseStockUtils.pre_stock_day(stock_days, intv, today)
	if lastN_stock_day is not None:
	    return lastN_stock_day.close >= lastN_stock_day.op
	return None


    #前第N个反弹日
    @staticmethod
    def pre_rebound_day(stock_days, intv, today):
        if len(stock_days) < intv:
            return None
	n = 0
	lastes_rebound_day_price = 0
	for stock_day in stock_days:
	    if stock_day.close > stock_day.op:
		if lastes_rebound_day_price == 0:
		    lastes_rebound_day_price = stock_day.close
		    n += 1
		else:
		    if stock_day.close > lastes_rebound_day_price:
			n += 1
			lastes_rebound_day_price = stock_day.close

	    if n == intv:
		return stock_day
	return None

    #前第N个反弹日(忽略当天)
    @staticmethod
    def pre_rebound_day_notoday(stock_days, intv, todaystamp):
	last1_is_red = BaseStockUtils.pre_is_red(stock_days, 1, todaystamp)		#昨日是否收红
	
	#昨日反弹阻力线
        if len(stock_days) < intv:
            return None
        n = 0
        lastes_rebound_day_price = 0
        for stock_day in stock_days:
            if stock_day.close > stock_day.op:
                if lastes_rebound_day_price == 0:
                    lastes_rebound_day_price = stock_day.close
                    n += 1
                else:
                    if stock_day.close > lastes_rebound_day_price:
                        n += 1
                        lastes_rebound_day_price = stock_day.close

            if n == intv:
                return stock_day
        return None


    @staticmethod
    def upper_shadow(stock_day):
	return round((stock_day.high - max(stock_day.op, stock_day.close)) / max(stock_day.op, stock_day.close), 5)

    @staticmethod
    def change_shadow(cur_stock_day, pre_stock_day):
	return round((cur_stock_day.close-pre_stock_day.close) / pre_stock_day.close, 5)

    @staticmethod
    def lower_shadow(stock_day):
	return round((min(stock_day.op, stock_day.close) - stock_day.low) / stock_day.low, 5)

    @staticmethod
    def change_shadow2(stock_day):
	return round((stock_day.close - stock_day.last_close) / stock_day.last_close, 5)

    @staticmethod
    def column_shadow(stock_day):
	return round((stock_day.close-stock_day.op) / stock_day.op, 5)

    #计算阻力位价格:日期从前往后
    @staticmethod
    def caculate_resitance_price((index1, rebound1_stock_day), (index2, rebound2_stock_day), index_t):
	if index1 is not None and index2 is not None and index_t is not None:

	    (t1, h1) = (index1, rebound1_stock_day.close)
	    (t2, h2) = (index2, rebound2_stock_day.close)
	    (t3, h3) = (index_t, 0)
	    h3 = round(h1 + (t3 - t1) * (h2 - h1) / (t2 - t1), 2)
#	    print (h1, h2, h3, t1, t2, t3)
	    rate = round((h2 - h1) / (t2 - t1), 2)
	    return (h3, rate)
	return None

    #计算多个阻力位
    @staticmethod
    def caculate_mutiple_resistance_prices(rebound_stock_days_tuple, index_t):
	resistance_prices = []
	try:
	    for i in range(len(rebound_stock_days_tuple)-1):
                for j in range(i+1, len(rebound_stock_days_tuple)):
                    resistance_prices.append(BaseStockUtils.caculate_resitance_price(rebound_stock_days_tuple[i], rebound_stock_days_tuple[j], index_t))
	    return resistance_prices
	except Exception, e:
	    LogUtils.info('BaseStockUtils[caculate_mutiple_resistance_prices], exception..' + str(e))
	return resistance_prices



    #最近的反弹日(不包括今天)
    @staticmethod
    def latest_rebound_stock_day(stock_days, stub_stock_day, is_with_stub):
	try:

	    base_stock_day = None
#	    print TimeUtils.timestamp2timestring(stub_stock_day.day)
	    index = -1
	    #定位起始位
	    for i in range(len(stock_days) -1):
#		print TimeUtils.timestamp2timestring(stock_days[i].day)
		if stock_days[i].day < stub_stock_day.day:
		    index = i
		if stock_days[i].day == stub_stock_day.day:
		    if is_with_stub:
			index = i
		    else:
			index = i + 1
		
		if index >= 0:
		    base_stock_day = stock_days[index]
		    break

#	    print 'latest_rebound_stock_day start index = ' + str(index)

	    if index >= 0:
		for i in range(index, len(stock_days) -1):
		    cur_stock_day = stock_days[i]
		    pre_stock_day = stock_days[i+1]
		    if cur_stock_day is not None and pre_stock_day is not None:
#			if (BaseStockUtils.column_shadow(cur_stock_day) > 0) and (cur_stock_day.close > base_stock_day.close):			#收红且高于昨日
			if (BaseStockUtils.change_shadow(cur_stock_day, pre_stock_day) > 0) and (cur_stock_day.close > max(base_stock_day.close, base_stock_day.op)):    #收涨且收盘价高于实体最高值
			    return (i, cur_stock_day)

	except Exception , e:
	    traceback.print_exc()
	    LogUtils.info('BaseStockUtils[latest_rebound_stock_day] exception...' + jsonpickle.encode(stub_stock_day))

	return None

    #多阻力位价格(不算当天的行情)
    @staticmethod
    def current_resistance_price(stock_days, stub_stock_day):
	(index1, latest1_rebound_day) = BaseStockUtils.latest_rebound_stock_day(stock_days, stub_stock_day, False)
	(index2, latest2_rebound_day) = BaseStockUtils.latest_rebound_stock_day(stock_days, latest1_rebound_day, True)
	(index3, latest3_rebound_day) = BaseStockUtils.latest_rebound_stock_day(stock_days, latest2_rebound_day, True)
	(index4, latest4_rebound_day) = BaseStockUtils.latest_rebound_stock_day(stock_days, latest3_rebound_day, True)
	index_t =  BaseStockUtils.index_of_stock_days(stock_days, stub_stock_day)
	resistance_prices = ((index1, latest1_rebound_day), (index2, latest2_rebound_day), (index3, latest3_rebound_day), (index4, latest4_rebound_day))
	return BaseStockUtils.caculate_mutiple_resistance_prices(resistance_prices, index_t)

    #最近的阻力位价格(不算当天的行情)
    @staticmethod
    def latest_resistance_price(stock_days, stub_stock_day):
	try:
	    #(index1, latest1_rebound_day)
	    latest1_rebound_day_tup = BaseStockUtils.latest_rebound_stock_day(stock_days, stub_stock_day, False)
#	    print latest1_rebound_day_tup
            if latest1_rebound_day_tup is None:
                return None
#	    print 'latest1_rebound_day_tuple : ' + jsonpickle.encode(latest1_rebound_day_tup)
	    latest2_rebound_day_tup = BaseStockUtils.latest_rebound_stock_day(stock_days, latest1_rebound_day_tup[1], True)
            if latest2_rebound_day_tup is None:
                return None
#	    print 'latest2_rebound_day_tuple : ' + jsonpickle.encode(latest2_rebound_day_tup)
	    index_t =  BaseStockUtils.index_of_stock_days(stock_days, stub_stock_day)
	
            if index_t is None:
                return None
#	    print 'target index = ' + str(index_t)
	
	    return BaseStockUtils.caculate_resitance_price(latest1_rebound_day_tup, latest2_rebound_day_tup, index_t)

	except Exception, e:
	    traceback.print_exc()
	return None

    #最近的收红日
    @staticmethod
    def latest_red_stock_day(stock_days, intv, todaystamp):
	cnt = 0
	for index in range(len(stock_days)):
	    lastN_is_red = BaseStockUtils.pre_is_red(stock_days, (index+1), todaystamp)
	    if lastN_is_red:
		cnt += 1

	    if cnt >= intv:
		return BaseStockUtils.pre_stock_day(stock_days, (index+1), todaystamp)
	return None

    @staticmethod
    def index_less_of(stock_days, todaystamp):
	for index in range(len(stock_days)):
	    if stock_days[index].day < todaystamp:
		return index
	return -1


    #目标日的索引位置:-1=最后预添加, [0-i]=目标索引,None=数据错误
    @staticmethod
    def index_of_stock_days(stock_days, stub_stock_day):
	is_exsit = True
        for i in range(len(stock_days)):
            if stock_days[i].day == stub_stock_day.day: 
                return i
	    if stock_days[i].day < stub_stock_day.day:
		return -1
	return None


    #是否冲破阻力位
    @staticmethod
    def is_cross_resistance(resistance_prices, realtime_stock_day):
		
	return False

    #均线黏合度
    @staticmethod
    def ma_hybridity(stock_days, realtime_stock_day):
	ma5 = IndicatorUtils.MA(stock_days, 5, realtime_stock_day)
	ma10 = IndicatorUtils.MA(stock_days, 10, realtime_stock_day)
	ma20 = IndicatorUtils.MA(stock_days, 20, realtime_stock_day)
	ma30 = IndicatorUtils.MA(stock_days, 30, realtime_stock_day)

    #封装当天交易分时数据(将历史交易数据与当天交易数据合并)
    @staticmethod
    def compose_realtime_stock_times(hist_times, realtime_stock_times):
#	print jsonpickle.encode(hist_times[len(hist_times) - 1]) + '\n'
#	print jsonpickle.encode(realtime_stock_times[0]) + '\n'
        current_hist_times = hist_times[:]
        if hist_times is None or len(hist_times) == 0:            #无历史数据，则直接返回当天数据
            current_hist_times = realtime_stock_times
        elif hist_times[len(hist_times) - 1].day < realtime_stock_times[0].day:             #当天记录未插入，则插入
            current_hist_times.extend(realtime_stock_times)
        else:                                                   #当天记录已插入，则更新
	    not_exist_stock_times = []
#	    print 'realtime_times : ' + jsonpickle.encode(realtime_stock_times[len(realtime_stock_times) - 1])
#	    print 'hist_times : ' + jsonpickle.encode(current_hist_times[len(current_hist_times) - 1])
	    for realtime_stock_time in realtime_stock_times:
		is_exist = False
		for hist_time in current_hist_times:
		    if hist_time.day == realtime_stock_time.day:
			is_exist = True
			break
		if not is_exist:
		    not_exist_stock_times.append(realtime_stock_time)
	    current_hist_times.extend(not_exist_stock_times)
	current_hist_times = sorted(current_hist_times, cmp=lambda x,y: cmp(x.day, y.day))        #时间轴顺序
        return current_hist_times



    #封装当天交易后周线数据
    @staticmethod
    def compose_realtime_stock_days(hist_days, realtime_stock_day):
	current_hist_days = hist_days[:]
	if hist_days is None or len(hist_days) == 0:		#无历史数据，则直接返回当天数据
	    current_hist_days = [realtime_stock_day]
	elif hist_days[0].day < realtime_stock_day:		#当天记录未插入，则插入
	    current_hist_days.insert(0, realtime_stock_day)
	else:							#当天记录已插入，则更新
	    current_hist_days[0] = realtime_stock_day
	return current_hist_days




    #封装当天交易后周线数据
    @staticmethod
    def compose_realtime_stock_weeks(hist_weeks, realtime_stock_day):
	current_hist_weeks = hist_weeks[:]
	if hist_weeks is not None and len(hist_weeks) > 0 and hist_weeks[0].day < realtime_stock_day:
	    if TimeUtils.is_same_week_with_datestamp(hist_weeks[0].day, realtime_stock_day.day):	#本周已存在记录,则计算本周数据
		last_period_day = current_hist_weeks[0]
		last_period_day.close = realtime_stock_day.close
		last_period_day.high = last_period_day.high if last_period_day.high > realtime_stock_day.high else realtime_stock_day.high
		last_period_day.low = last_period_day.low if last_period_day.low < realtime_stock_day.low else realtime_stock_day.low
		last_period_day.day = realtime_stock_day.day
		last_period_day.money = last_period_day.money + realtime_stock_day.money
		last_period_day.vol = last_period_day.vol + realtime_stock_day.vol
		
	    else:										#本周不存在记录
	    	last_period_day = realtime_stock_day
		last_period_day.id = realtime_stock_day.symbol + TimeUtils.timestamp2datestring(TimeUtils.current_friday_from_datestamp(realtime_stock_day.day))
		current_hist_weeks.insert(0, last_period_day)
	return current_hist_weeks



    #封装当天交易后周线数据
    @staticmethod
    def compose_realtime_stock_months(hist_months, realtime_stock_day):
        current_hist_months = hist_months[:]
        if hist_months is not None and len(hist_months) > 0 and hist_months[0].day < realtime_stock_day:
            if TimeUtils.is_same_month_with_datestamp(hist_months[0].day, realtime_stock_day.day):    #本周已存在记录
                last_period_day = current_hist_months[0]
                last_period_day.close = realtime_stock_day.close
                last_period_day.high = last_period_day.high if last_period_day.high > realtime_stock_day.high else realtime_stock_day.high
                last_period_day.low = last_period_day.low if last_period_day.low < realtime_stock_day.low else realtime_stock_day.low
                last_period_day.day = realtime_stock_day.day
                last_period_day.money = last_period_day.money + realtime_stock_day.money
                last_period_day.vol = last_period_day.vol + realtime_stock_day.vol
            else:                                                                               #本周不存在记录
                last_period_day = realtime_stock_day
                last_period_day.id = realtime_stock_day.symbol + TimeUtils.timestamp2datestring(TimeUtils.lastday_of_month_from_datestamp(realtime_stock_day.day))
                current_hist_months.insert(0, last_period_day)
        return current_hist_months

    #封装分时数据，如5分钟，15分钟，30分钟，60分钟
    @staticmethod
    def compose_stock_trades_for_minute(hist_trades, intv):	#顺时针
	com_stock_trades = []
	tmp_stock_min = StockTimeInfo()
	tmp_stock_min.low = 99999999
	tmp_stock_min.op = hist_trades[0].close

	start_min = hist_trades[0].day
	
	for loop in range(0, len(hist_trades)):
	    hist_trade = hist_trades[loop]
	    tmp_stock_min.vol += hist_trade.vol
	    tmp_stock_min.money += hist_trade.money
	    tmp_stock_min.close = hist_trade.close
	    tmp_stock_min.high = hist_trade.close if hist_trade.close > tmp_stock_min.high else tmp_stock_min.high
	    tmp_stock_min.low = hist_trade.close if hist_trade.close < tmp_stock_min.low else tmp_stock_min.low

            tmp_stock_min.day = hist_trade.day
            tmp_stock_min.id = hist_trade.id
	    tmp_stock_min.symbol = hist_trade.symbol


	    if loop > 0 and ( (hist_trade.day - start_min)/60  % intv) == 0:	#loop判断是为了将9点半的数据累计到后5分钟
		com_stock_trades.append(tmp_stock_min)

		tmp_stock_min = StockTimeInfo()
		tmp_stock_min.low = 99999999
		tmp_stock_min.op = hist_trades[loop + 1].close if loop < len(hist_trades)-1 else None
	
		day_str = TimeUtils.timestamp2datestring(hist_trade.day)
		if TimeUtils.timestamp2timestring(hist_trade.day) == (day_str + ' 11:30:00'):			#如果当前游标在午盘休市时间节点，则将起始时间设为午盘开市
		    start_min = TimeUtils.timestring2timestamp(day_str + ' 13:00:00')
		else:
		    start_min = hist_trade.day

	    else:
	        if loop == len(hist_trades)-1:
                    com_stock_trades.append(tmp_stock_min)
	return com_stock_trades

    #根据日分时交易数据封装realtime_stock_day
    @staticmethod
    def compose_realtime_stock_day_from_time_trades(stock_times, last_close=None, symbol=None, today_stamp=None):
	if stock_times is not None:
	    realtime_stock_day = StockDayInfo()
	    realtime_stock_day.op = stock_times[0].close
	    realtime_stock_day.high = max([stock_time.close for stock_time in stock_times])
	    realtime_stock_day.low = min([stock_time.low for stock_time in stock_times])
	    realtime_stock_day.close = stock_times[len(stock_times) - 1].close
	    realtime_stock_day.vol = sum([stock_time.vol for stock_time in stock_times]) 
	    realtime_stock_day.money = sum([stock_time.money for stock_time in stock_times])
	    realtime_stock_day.last_close = last_close
	    realtime_stock_day.day = today_stamp
	    realtime_stock_day.id = symbol + TimeUtils.datestamp2datestring(today_stamp, TimeUtils.DATE_FORMAT_YYYYMMDD)
	    realtime_stock_day.symbol = symbol
	    return realtime_stock_day
	return None

    # 封装命中数据格式
    @staticmethod
    def compose_hit_data(realtime_stock_day, model_tup):
	return (realtime_stock_day.symbol, realtime_stock_day.op, realtime_stock_day.high, realtime_stock_day.low, realtime_stock_day.close, realtime_stock_day.last_close) +  model_tup

