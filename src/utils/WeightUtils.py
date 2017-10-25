#encoding=utf-8

from utils.BaseStockUtils import *

class WeightUtils:

    @staticmethod
    def caculate_weight(hist_days, realtime_stock_day, model):
	if model[0].find('Burst') >= 0:
	    return WeightUtils.weight_for_burst(hist_days, realtime_stock_day, model)
	elif model[0].find('RT') >= 0:
	    return WeightUtils.weight_for_rt(hist_days, realtime_stock_day, model)
	return 0


    @staticmethod
    def weight_for_burst(hist_days, realtime_stock_day, model):			#model:(model_name, resistance, ratio)
	weight = 0
	index = -1
	for i in range(len(hist_days)):
	    if hist_days[i].day < realtime_stock_day.day:
		index = i
		break

	if hist_days[index].close < hist_days[index].op or hist_days[index].close < hist_days[index].last_close:
	    weight += 1

	if realtime_stock_day.high > 1.01 * model[1]:
	    weight += 0.3

	if realtime_stock_day.close > 1.003 * model[1]:
	    weight += 0.3

	return weight



    @staticmethod
    def weight_for_rt(hist_days, realtime_stock_day, model):                 #model:(model_name,)
        weight = 0
        index = -1
        for i in range(len(hist_days)):
            if hist_days[i].day < realtime_stock_day.day:
                index = i
                break

        if BaseStockUtils.upper_shadow(hist_days[index]) > 0.02:
            weight += 1


        return weight


    @staticmethod
    def calc_weight(hist_days, realtime_stock_day):
        try:
            index = -1
            for i in range(len(hist_days)):
                if hist_days[i].day < realtime_stock_day.day:
                    index = i
                    break

            weight = 0
            #rt
            if abs(BaseStockUtils.upper_shadow(hist_days[index])) > 0.02:
                weight = weight + 1

            #star
	    if abs(BaseStockUtils.column_shadow(hist_days[index])) < 0.01:
		weight = weight + 1

	    #minv
	    if realtime_stock_day.low > 0.985 * min(realtime_stock_day.op, realtime_stock_day.last_close) and hist_days[index].close > hist_days[index].op:
		weight = weight + 1

	    #burst
	    latest_resistance_price_tup = BaseStockUtils.latest_resistance_price(hist_days, realtime_stock_day)
	    if latest_resistance_price_tup is not None and realtime_stock_day.close > 1.003 * latest_resistance_price_tup[0]:
		weight = weight + 3

	    return weight 

	except Exception, e:
	    traceback.print_exc()
