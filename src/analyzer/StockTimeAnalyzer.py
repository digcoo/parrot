# encoding=utf8  
import time
import sys
import jsonpickle
import traceback

from vo.StockInfo import *
from utils.ParseUtil import *
from dbs.GeodeClient import *
from utils.BaseStockUtils import *
from utils.LogUtils import *
from dto.DataContainer import *

from quant.ModelTimeMA import *
from quant.ModelTime30 import *
from quant.ModelTimeRise import *
from quant.ModelTimeMin import *

from StockDayPackMatcher import *

class StockTimeAnalyzer:

    def __init__(self, symbols, todaystamp):
	try:
#	    LogUtils.info('==============cache_hist_time start========================================')
            start  = int(time.mktime(datetime.datetime.now().timetuple()))

            self.todaystamp = todaystamp
	    self.data_container = DataContainer(symbols)

#            LogUtils.info('cache_hist_time take %s seconds' % (str(end - start), ))
#	    LogUtils.info('==============cache_hist_times end========================================\n\n\n')



#            LogUtils.info('==============stock_time_analyzer_model_init start========================================')
	    start  = int(time.mktime(datetime.datetime.now().timetuple()))

	    self.model_time_ma = ModelTimeMA(self.data_container.hist_times, self.todaystamp)
	    self.model_time_30 = ModelTime30(self.data_container.hist_days, self.data_container.hist_times, self.todaystamp)
	    self.model_time_rise = ModelTimeRise(self.data_container.hist_days, self.data_container.hist_times, self.todaystamp)
	    self.model_time_min = ModelTimeMin(self.data_container.hist_days, self.data_container.hist_times, self.todaystamp)

	    self.stock_day_pack_matcher = StockDayPackMatcher(symbols, todaystamp, self.data_container)

	    end2= int(time.mktime(datetime.datetime.now().timetuple()))
#	    LogUtils.info('stock_time_analzer_model_init take %s seconds' % (str(end - start), ))
#	    LogUtils.info('==============stock_time_analyzer_model_init end========================================\n\n\n')

	except Exception, e:
	    traceback.print_exc()
	    sys.exit()


    #模型匹配
    def match(self, realtime_stock_trades_map):		#model_tup:(symbol, day_times)
	match_model = None

	try:

	    symbol = realtime_stock_trades_map.get('symbol')
	    last_close = realtime_stock_trades_map.get('last_close')
	    today_stamp = realtime_stock_trades_map.get('today_stamp')

	    today_times = realtime_stock_trades_map.get(symbol)
	    realtime_stock_day = BaseStockUtils.compose_realtime_stock_day_from_time_trades(today_times, symbol=symbol, last_close=last_close, today_stamp=today_stamp)

#	    match_model = self.add_match_model(match_model, self.model_time_ma.match(realtime_stock_trades_map))  #ModelTimeMA(TimeMA)
	    match_model = self.add_match_model(match_model, self.model_time_30.match(realtime_stock_day, today_times))  #ModelTime30(Time30)
#	    match_model = self.add_match_model(match_model, self.model_time_rise.match(realtime_stock_day, today_times))  #ModelTimeRise(TimeRise)
	    match_model = self.add_match_model(match_model, self.model_time_min.match(realtime_stock_day, today_times))  #ModelTimeMin(TimeMin)


            match_model = self.add_match_model(match_model, self.stock_day_pack_matcher.match(realtime_stock_day))


            if match_model is not None  and self.filter_common_indicate(realtime_stock_day, match_model[0]):
                return BaseStockUtils.compose_hit_data(realtime_stock_day, match_model)

	except Exception, e:
	    traceback.print_exc()

	return None

    def add_match_model(self,  ret_source_model, add_model):
	if ret_source_model is None:
	    return add_model
	elif add_model is None:
	    return ret_source_model
	else:
	    return (ret_source_model[0] + ',' + add_model[0],)

    def filter_common_indicate(self, realtime_stock_day, match_model):
        try:
	    return True

            hist_weeks = self.latest_weeks[realtime_stock_day.symbol]
            hist_days = self.latest_days[realtime_stock_day.symbol]
            hist_months = self.latest_months[realtime_stock_day.symbol]

            last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
            if last1_stock_day is None:
                return None

            current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)
            current_hist_weeks = BaseStockUtils.compose_realtime_stock_weeks(hist_weeks, realtime_stock_day)
            current_hist_months = BaseStockUtils.compose_realtime_stock_months(hist_months, realtime_stock_day)


            current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)
            current_hist_weeks = BaseStockUtils.compose_realtime_stock_weeks(hist_weeks, realtime_stock_day)
            current_hist_months = BaseStockUtils.compose_realtime_stock_months(hist_months, realtime_stock_day)

            last1_above_pressure_month_ma = IndicatorUtils.above_pressure_ma_tup(hist_months, self.todaystamp, realtime_stock_day.close)          #上月K线阻力位
            last0_above_pressure_month_ma = IndicatorUtils.above_pressure_ma_tup(hist_months, TimeUtils.date_add(TimeUtils.lastday_of_month_from_datestamp(self.todaystamp), 1), realtime_stock_day.close)        #本月K线阻力位
            last1_above_pressure_week_ma = IndicatorUtils.above_pressure_ma_tup(hist_weeks, self.todaystamp, realtime_stock_day.close)        #上周K线阻力位
            last0_above_pressure_week_ma = IndicatorUtils.above_pressure_ma_tup(hist_weeks, TimeUtils.date_add(self.todaystamp, 7), realtime_stock_day.close)        #本周K线阻力位
            last1_above_pressure_daily_ma = IndicatorUtils.above_pressure_ma_tup(hist_days, self.todaystamp, realtime_stock_day.close)          #昨日上方阻力位
            last0_above_pressure_daily_ma = IndicatorUtils.above_pressure_ma_tup(current_hist_days, TimeUtils.date_add(self.todaystamp, 7), realtime_stock_day.close)  #当天实时上方阻力位


	    last0_ma5 = IndicatorUtils.MA(current_hist_days, 5, self.todaystamp)

            is_hit = True

            is_last0_month_over_pressure = (last0_above_pressure_month_ma is None or realtime_stock_day.close < 0.96 * last0_above_pressure_month_ma[1])   #价格远离本月阻力至少5个点
#            is_hit = is_hit & (is_last0_month_over_pressure)

            #过滤本周周k线阻力位
            is_last0_week_over_pressure = (last0_above_pressure_week_ma is None or realtime_stock_day.close < 0.97 * last0_above_pressure_week_ma[1])   #当前价格远离本周阻力至少4个点
#            is_hit = is_hit & (is_last0_week_over_pressure)

            #过滤当日日k线阻力位
#           LogUtils.info('symbol = ' + realtime_stock_day.symbol + ', daily pressure = ' + str(last1_above_pressure_daily_ma) + ', current close = ' + str(realtime_stock_day.close))
            is_last0_daily_over_pressure = (last0_above_pressure_daily_ma is None or realtime_stock_day.close < 0.98 * last0_above_pressure_daily_ma[1])  #价格远离上方阻力至少3个点
#            is_hit = is_hit & (is_last0_daily_over_pressure)

            #过滤开盘即涨停
#            is_hit = is_hit & (realtime_stock_day.high > realtime_stock_day.low)

            #收红
#            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)

            #过滤向下价格偏离
#            is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * last1_stock_day.close)         #均价高于昨日收盘价
#            is_hit = is_hit & (realtime_stock_day.close > 0.994 * last1_stock_day.close)         #当前价格高于昨日收盘价
#            is_hit = is_hit & (realtime_stock_day.close > 0.996 * realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价
#	    is_hit = is_hit & (realtime_stock_day.close > last0_ma5)							#当前价格高于MA5


#           if not is_hit:
#               LogUtils.info('filter symbol :' + realtime_stock_day.symbol + ', model = ' + match_model)

            return is_hit

        except Exception, e:
            traceback.print_exc()
        return None

