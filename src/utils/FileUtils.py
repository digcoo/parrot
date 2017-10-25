#encoding=utf-8

import traceback
import csv
import os
import jsonpickle as json

from utils.TimeUtils import *

class FileUtils:

    output_dir = '/home/ubuntu/backtest_result'
    head_data = ['股票代码', '买入日', '买入价', '实体柱', '上影线', '下影线',  '卖出日', '卖出价', '当日卖出最高赢利', '当日卖出最大亏损比例',  '收盘盈亏比例', '赢/亏']

    #csv模板：股票代码，买入日，买入价，买入当天涨幅，卖出日，卖出价，最高涨幅，最低涨幅，收盘涨幅，是否亏损
    @staticmethod
    def output_backup_test(symbol, model, hist_days, indexs, test_days):		#index[list]=所有购买日， test_days=回测天数
	try:

	    lines_data = FileUtils.compose_lines_data(symbol, hist_days, indexs, test_days)
	    FileUtils.output_lines_data(lines_data, model)
	    
	except Exception, e:
            traceback.print_exc()

    @staticmethod
    def output_lines_data(lines_data, model, symbol):
	csv_file = None
	try:

            final_dir = FileUtils.output_dir + '/' + model
            if not os.path.exists(final_dir):
                os.makedirs(final_dir)

            if lines_data is not None and len(lines_data) > 0:
                (total_profit, profit_cnt, total_cnt) = FileUtils.calculate_sum(lines_data)
                print symbol + ', total_profile=' + str(total_profit) + ', profit_cnt=' + str(profit_cnt) + ', total_cnt=' + str(total_cnt)
                csv_file = open(final_dir + '/' + model + '_' + symbol + '.csv', 'wb')
                writer = csv.writer(csv_file)
		
		#头部header
                writer.writerow(FileUtils.head_data)

                for line_data in lines_data:
                    writer.writerow(line_data)

	except Exception, e:
	    traceback.print_exc()

        finally:
            if csv_file is not None:
                csv_file.close()


    @staticmethod
    def compose_lines_data(symbol, hist_days, indexs, test_days):
	lines_data = []
	for index in indexs:
	    if index >= test_days:
		data_line = FileUtils.compose_line_data_array(symbol, hist_days[index], hist_days[index-test_days])
		lines_data.append(data_line)
	return lines_data
		

    #顺序被打乱
    @staticmethod
    def compose_line_data(symbol, buy_stock_day, sell_stock_day):
	line_data = {}
	line_data['symbol']=symbol
	line_data['buy_day']=TimeUtils.timestamp2datestring(buy_stock_day.day)
	line_data['buy_price']=buy_stock_day.close
	line_data['buy_column_shadow']=  str(round((buy_stock_day.close-buy_stock_day.op)/buy_stock_day.op * 100, 2)) + '%'
	
        line_data['sell_day']=TimeUtils.timestamp2datestring(sell_stock_day.day)
        line_data['sell_price']=sell_stock_day.close
        line_data['sell_column_shadow']=str(round((sell_stock_day.high-buy_stock_day.close)/buy_stock_day.close * 100, 2)) + '%'

	line_data['final_profit_shadow']=str(round((sell_stock_day.close-buy_stock_day.close)/buy_stock_day.close * 100, 2)) + '%'
	line_data['profit_or_loss']='赢' if sell_stock_day.close>buy_stock_day.close else '亏'

	return line_data

    #顺序被打乱
    @staticmethod
    def compose_line_data_array(symbol, buy_stock_day, sell_stock_day):
        line_data = []
        line_data.append(symbol)
        line_data.append(TimeUtils.timestamp2datestring(buy_stock_day.day))			#买入日
	line_data.append(buy_stock_day.close)							#收盘买入价
	line_data.append(round((buy_stock_day.close-buy_stock_day.op)/buy_stock_day.op * 100, 2))	#收盘实体
	line_data.append(round((buy_stock_day.high-buy_stock_day.close)/buy_stock_day.close * 100, 2))	#上影线
        line_data.append(round((buy_stock_day.op-buy_stock_day.low)/buy_stock_day.low * 100, 2))  #下影线

	
	line_data.append(TimeUtils.timestamp2datestring(sell_stock_day.day))			#卖出日
	line_data.append(sell_stock_day.close)							#卖出价
	line_data.append(round((sell_stock_day.high-buy_stock_day.close)/buy_stock_day.close * 100, 2))		#卖出最高收益
        line_data.append(round((sell_stock_day.low-buy_stock_day.close)/buy_stock_day.close * 100, 2))         #卖出最高亏损

	
	line_data.append(round((sell_stock_day.close-buy_stock_day.close)/buy_stock_day.close * 100, 2))	#尾盘卖出收益
	line_data.append('赢' if sell_stock_day.close>buy_stock_day.close else '亏')	

        return line_data

    #统计数据
    @staticmethod
    def calculate_sum(lines_data):
	total_profit = 0
	profit_cnt = 0
	total_cnt = 0
	for line_data in lines_data:
	    total_cnt += 1
	    total_profit += line_data[10]
	    if line_data[10] > 0:
		profit_cnt += 1

	return (total_profit, profit_cnt, total_cnt)


if __name__ == '__main__':
    final_dir = FileUtils.output_dir + '/model'
    if not os.path.exists(final_dir):
	os.makedirs(final_dir)
    csv_file = open(FileUtils.output_dir + '/model/' + 'symbol' + '.csv', 'wb')
#    writer = csv.writer(csv_file, delimiter=',', quotechar="'", quoting=csv.QUOTE_ALL)
    writer = csv.writer(csv_file)
    my_dict =  {'PCIP': '192.168.1.4', 'DutIP': '192.168.1.6', 'timestamp': '20120410100340'}
    print type(my_dict.viewvalues())
    print list(my_dict.viewvalues())
    writer.writerow(list(my_dict.viewvalues()))
    csv_file.close()
