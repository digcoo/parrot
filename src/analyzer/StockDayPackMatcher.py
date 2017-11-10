# encoding=utf8  
import time
import jsonpickle
import traceback
from vo.StockInfo import *
from utils.ParseForSinaUtils import *
from utils.IndicatorUtils import *
from dbs.GeodeClient import *
from utils.BaseStockUtils import *
from utils.LogUtils import *

from quant.ModelBoard import *
from quant.ModelUpper import *
from quant.ModelCover import *
from quant.ModelBurst import *
from quant.ModelMinV import *
from quant.ModelLastBreak import *
from quant.ModelReMarket import *
from quant.ModelBase import *
from quant.ModelDWMMA import *
from quant.ModelCWMMA import *
from quant.ModelCLWMMA import *
from quant.ModelMAScatter import *

class StockDayPackMatcher:

    def __init__(self, symbols, todaystamp, data_container):
	try:
	    LogUtils.info('==============cache_hist_days_and_weeks start========================================')
            start  = int(time.mktime(datetime.datetime.now().timetuple()))

            self.todaystamp = todaystamp
            self.latest_days = data_container.hist_days
            self.latest_weeks = data_container.hist_weeks
	    self.latest_months = data_container.hist_months

            end = int(time.mktime(datetime.datetime.now().timetuple()))
            LogUtils.info('cache_hist_days_and_weeks take %s seconds' % (str(end - start), ))
	    LogUtils.info('==============cache_hist_days_and_weeks end========================================\n\n\n')


            LogUtils.info('==============model_init start========================================')
	    start  = int(time.mktime(datetime.datetime.now().timetuple()))


	    self.model_board = ModelBoard(self.todaystamp)
	    self.model_upper = ModelUpper(self.latest_days, self.todaystamp)
	    self.model_ma_scatter = ModelMAScatter(self.latest_days, self.todaystamp)
	    self.model_min_v = ModelMinV(self.latest_days, self.todaystamp)
	    self.model_burst = ModelBurst(self.latest_days, self.todaystamp)
	    self.model_last_break = ModelLastBreak(self.latest_days, self.todaystamp)
	    self.model_cover = ModelCover(self.latest_days, self.todaystamp)
            self.model_re_market = ModelReMarket(self.latest_days, data_container, self.todaystamp)
	    self.model_base = ModelBase(self.latest_days, self.latest_weeks, self.latest_months, self.todaystamp)
	    self.model_dwm_ma = ModelDWMMA(self.latest_days, self.latest_weeks, self.todaystamp)
	    self.model_cwm_ma = ModelCWMMA(self.latest_days, self.latest_weeks, self.latest_months, self.todaystamp)
	    self.model_clwm_ma = ModelCLWMMA(self.latest_days, self.latest_weeks, self.latest_months, self.todaystamp)
	    

	    end2= int(time.mktime(datetime.datetime.now().timetuple()))
	    LogUtils.info('model_init take %s seconds' % (str(end - start), ))
	    LogUtils.info('==============model_init end========================================\n\n\n')

	except Exception, e:
	    traceback.print_exc()
	    sys.exit()


    #模型匹配
    def match(self, realtime_stock_day):		#model_tup:(model_name, weight)
	match_model = None
	try:
	    match_model = self.add_match_model(match_model, self.model_board.match(realtime_stock_day)) #ModelBoard(Board)
	    match_model = self.add_match_model(match_model, self.model_upper.match(realtime_stock_day))	#ModelUpper(Upper)
	    match_model = self.add_match_model(match_model, self.model_ma_scatter.match(realtime_stock_day)) #ModelMAScatter(MAScatter)
            match_model = self.add_match_model(match_model, self.model_cover.match(realtime_stock_day))  #ModelCover(Cover)
	    match_model = self.add_match_model(match_model, self.model_min_v.match(realtime_stock_day))  #ModelMinV(MinV)
	    match_model = self.add_match_model(match_model, self.model_burst.match(realtime_stock_day))  #ModelBurst(Burst)
	    match_model = self.add_match_model(match_model, self.model_last_break.match(realtime_stock_day))  #ModelLastBreak(LBreak)
            match_model = self.add_match_model(match_model, self.model_re_market.match(realtime_stock_day))  #ModelReMarket(ReMark)
	    match_model = self.add_match_model(match_model, self.model_base.match(realtime_stock_day))  #ModelBase(Base)
	    match_model = self.add_match_model(match_model, self.model_dwm_ma.match(realtime_stock_day))  #ModelDWMMA(DWM)
	    match_model = self.add_match_model(match_model, self.model_cwm_ma.match(realtime_stock_day))  #ModelCWMMA(CWM)
	    match_model = self.add_match_model(match_model, self.model_clwm_ma.match(realtime_stock_day))  #ModelCLWMMA(CLWM)

            if match_model is not None and self.filter_common_indicate(realtime_stock_day, match_model[0]):
		return match_model

	except Exception, e:
	    traceback.print_exc()

	return None

    #过滤阻力位
    def filter_common_indicate(self, realtime_stock_day, match_model):
        try:

	    #忽略
#	    if match_model.find('ReMark-') > -1 or match_model.find('Upper-') > -1 or match_model.find('Cover-') > -1  or match_model.find('MAScatter-') > -1 or match_model.find('Board-') > -1:

#		return True

            hist_weeks = self.latest_weeks[realtime_stock_day.symbol]
	    hist_days = self.latest_days[realtime_stock_day.symbol]
	    hist_months = self.latest_months[realtime_stock_day.symbol]

	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)
	    if last1_stock_day is None:
		return None

            current_hist_days = BaseStockUtils.compose_realtime_stock_days(hist_days, realtime_stock_day)
	    current_hist_weeks = BaseStockUtils.compose_realtime_stock_weeks(hist_weeks, realtime_stock_day)
	    current_hist_months = BaseStockUtils.compose_realtime_stock_months(hist_months, realtime_stock_day)

	    last1_above_pressure_month_ma = IndicatorUtils.above_pressure_ma_tup(hist_months, self.todaystamp, realtime_stock_day.close)          #上月K线阻力位
	    last0_above_pressure_month_ma = IndicatorUtils.above_pressure_ma_tup(hist_months, TimeUtils.date_add(TimeUtils.lastday_of_month_from_datestamp(self.todaystamp), 1), realtime_stock_day.close)        #本月K线阻力位
	    last1_above_pressure_week_ma = IndicatorUtils.above_pressure_ma_tup(hist_weeks, self.todaystamp, realtime_stock_day.close)        #上周K线阻力位
            last0_above_pressure_week_ma = IndicatorUtils.above_pressure_ma_tup(hist_weeks, TimeUtils.date_add(self.todaystamp, 7), realtime_stock_day.close)        #本周K线阻力位
	    last1_above_pressure_daily_ma = IndicatorUtils.above_pressure_ma_tup(hist_days, self.todaystamp, realtime_stock_day.close)          #昨日上方阻力位
	    last0_above_pressure_daily_ma = IndicatorUtils.above_pressure_ma_tup(current_hist_days, TimeUtils.date_add(self.todaystamp, 7), realtime_stock_day.close)          #当天实时上方阻力位
	    
            is_hit = True
#	    LogUtils.info('symbol = ' + realtime_stock_day.symbol + ', monthly pressure = ' + str(last0_above_pressure_month_ma) + ', current close = ' + str(realtime_stock_day.close))
	    is_last0_month_over_pressure = (last0_above_pressure_month_ma is None or realtime_stock_day.close < 0.95 * last0_above_pressure_month_ma[1])   #价格远离本月阻力至少5个点
	    is_hit = is_hit & (is_last0_month_over_pressure)

	    #过滤本周周k线阻力位
#	    LogUtils.info('symbol = ' + realtime_stock_day.symbol + ', weekly pressure = ' + str(last0_above_pressure_week_ma) + ', current close = ' + str(realtime_stock_day.close))
            is_last0_week_over_pressure = (last0_above_pressure_week_ma is None or realtime_stock_day.close < 0.96 * last0_above_pressure_week_ma[1])	#当前价格远离本周阻力至少4个点
	    is_hit = is_hit & (is_last0_week_over_pressure)
	
	    #过滤当日日k线阻力位
#	    LogUtils.info('symbol = ' + realtime_stock_day.symbol + ', daily pressure = ' + str(last1_above_pressure_daily_ma) + ', current close = ' + str(realtime_stock_day.close))
	    is_last0_daily_over_pressure = (last0_above_pressure_daily_ma is None or realtime_stock_day.close < 0.97 * last0_above_pressure_daily_ma[1])  #价格远离上方阻力至少3个点
	    is_hit = is_hit & (is_last0_daily_over_pressure)

	    #过滤开盘即涨停
	    is_hit = is_hit & (realtime_stock_day.high > realtime_stock_day.low)

            #高于最低日MA线
	    is_hit = is_hit & (realtime_stock_day.close > IndicatorUtils.Lowest_MA(current_hist_days, self.todaystamp))                 #昨日收盘价高于最低ma线

	    #收红
	    is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)

	    #过滤向下价格偏离
            is_hit = is_hit & (realtime_stock_day.money/realtime_stock_day.vol > 0.994 * last1_stock_day.close)         #均价高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > 0.994 * last1_stock_day.close)         #当前价格高于昨日收盘价
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.money/realtime_stock_day.vol)      #当前价格高于均价


#	    if not is_hit:
#		LogUtils.info('filter symbol :' + realtime_stock_day.symbol + ', model = ' + match_model)

            return is_hit

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

