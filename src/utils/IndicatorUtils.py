#encoding=utf-8
import traceback
import jsonpickle

from utils.LogUtils import *
from utils.BaseStockUtils import *
from utils.TimeUtils import *

class IndicatorUtils:

    '''
    @staticmethod
    def MA(hist_days, ndays, todaystamp):
        try:
	    total = 0
	    tmp_cnt = 0
	    for i in range(len(hist_days)):
		stock_day = hist_days[i]
#		LogUtils.info('cursor stock_day = ' + stock_day.id + ', todaystamp = ' + str(TimeUtils.timestamp2datestring(todaystamp)))
		if todaystamp == 0 or stock_day.day < todaystamp:
#		    LogUtils.info('MA: id = ' + stock_day.id)
		    total = total + stock_day.close
#		    LogUtils.info('total = ' + str(total) + ', close = ' + str(stock_day.close))
		    tmp_cnt = tmp_cnt + 1

		    if tmp_cnt == ndays:
			return round(total / ndays, 5)

	    return None
        except Exception, e:
            traceback.print_exc()
	return None
    '''

    @staticmethod
    def MA(hist_days, ndays, todaystamp):
        try:
            total = 0
            tmp_cnt = 0
            for i in range(len(hist_days)):
                stock_day = hist_days[i]
#               LogUtils.info('cursor stock_day = ' + stock_day.id + ', todaystamp = ' + str(TimeUtils.timestamp2datestring(todaystamp)))
                if todaystamp == 0 or stock_day.day < todaystamp:
#                   LogUtils.info('MA: id = ' + stock_day.id)
                    total = total + stock_day.close
#                   LogUtils.info('total = ' + str(total) + ', close = ' + str(stock_day.close))
                    tmp_cnt = tmp_cnt + 1

                    if tmp_cnt == ndays:
                        return round(total / ndays, 5)
		
		    if i == len(hist_days) - 1:
			return round(total / tmp_cnt, 5)

            return None
        except Exception, e:
            traceback.print_exc()
        return None


    @staticmethod
    def ALL_MA(hist_days, todaystamp):
	try:
	    MA5 = IndicatorUtils.MA(hist_days, 5, todaystamp)
#	    LogUtils.info('MA5 = ' + str(MA5))
	    MA10 = IndicatorUtils.MA(hist_days, 10, todaystamp)
#	    LogUtils.info('MA10 = ' + str(MA10))
	    MA20 = IndicatorUtils.MA(hist_days, 20, todaystamp)
#	    LogUtils.info('MA20 = ' + str(MA20))
	    MA30 = IndicatorUtils.MA(hist_days, 30, todaystamp)
#	    LogUtils.info('MA30 = ' + str(MA30))
	    return max(MA5, MA10, MA20, MA30)
	except Exception, e:
	    traceback.print_exc()
	return None

    #EMA(X，4)=［2*X4+(4-1)*Y’］/(4+1)
    @staticmethod
    def EMA(hist_days, ndays, todaystamp):
	try:
	    for i in range(len(hist_days)):
                stock_day = hist_days[i]
                if todaystamp == 0 or stock_day.day <= todaystamp:
		    if i == len(hist_days) - 1:
			return 100
		    else:
		        return (2 * stock_day.close + (ndays-1) * (IndicatorUtils.EMA(hist_days, ndays, hist_days[i+1].day))) / (ndays + 1)

	except Exception, e:
	    traceback.print_exc()

    @staticmethod
    def DIF(hist_days, intv, todaystamp):
        try:
	    print ''            
        except Exception, e:
            traceback.print_exc()


    def RSV(hist_days, ndays, todaystamp):
	try:
	    print ''
	except Exception, e:
	    traceback.print_exc()

    @staticmethod
    def KDJ(hist_days, ndays, todaystamp):
        try:
            total = 0
            tmp_cnt = 0
	    Hn = 0
	    Ln = 0
	    Cn = 0
            for i in range(len(hist_days)):
                stock_day = hist_days[i]
                if todaystamp == 0 or stock_day.day <= todaystamp:
		    if stock_day.high > Hn:
			Hn = stock_day.high

		    if stock_day.low < Ln:
			Ln = stock_day.low

		    if Cn == 0:
			Cn = stock_day.close

		    tmp_cnt = tmp_cnt + 1
		    if tmp_cnt == ndays:
			break

	    nRSV = (Cn - Ln) / (Hn - Ln) * 100
#	    nK = 


        except Exception, e:
            traceback.print_exc()

    @staticmethod
    def above_pressure_ma_tup(hist_days, todaystamp, cur_price):
	try:
	    MA5 = IndicatorUtils.MA(hist_days, 5, todaystamp)
	    MA10 = IndicatorUtils.MA(hist_days, 10, todaystamp)
	    MA20 = IndicatorUtils.MA(hist_days, 20, todaystamp)
	    MA30 = IndicatorUtils.MA(hist_days, 30, todaystamp)
	    ma_list = []
	    if MA5 is not None:
		ma_list.append(('MA5', MA5))
            if MA10 is not None:
                ma_list.append(('MA10', MA10))
            if MA20 is not None:
                ma_list.append(('MA20', MA20))
            if MA30 is not None:
                ma_list.append(('MA30', MA30))
	
#	    sorted(ma_list, key=lambda ma:ma[1])
#	    print '[above_pressure_ma_tup], before, symbol =  ' + hist_days[0].symbol + ', all_ma_list = ' + jsonpickle.encode(ma_list)
	    ma_list = sorted(ma_list, cmp=lambda x,y: cmp(x[1], y[1]))
#	    print '[above_pressure_ma_tup], after, symbol =  ' + hist_days[0].symbol + ', all_ma_list = ' + jsonpickle.encode(ma_list) + '\n\n'
	    for ma in ma_list:
		if cur_price < ma[1]:
		    return ma

	except Exception, e:
	    traceback.print_exc()
	return None
	
