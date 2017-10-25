#encoding=utf-8

from sys import path
path.append('/home/ubuntu/scripts')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/quant/incubation')

from CommonUtils import *
from TimeUtils import *
from FileUtils import *
from ModelClose import *
from ModelCloseGreenRT import *
from ModelCloseT import *
from ModelCloseBRedHead import *
from ModelCloseSRedHead import *
from ModelVol import *


class CloseTest:

    #一支票的历史记录
    def __init__(self, hist_days, symbol, test_days):
	self.hist_days = hist_days
	self.symbol = symbol
	self.test_days = test_days

    def test(self):
	if self.hist_days is not None:
#	    self.test_for_close_green_rt()			#大阴后收盘翻红
#	    self.test_for_close_t()				#吊脚线
#	    self.test_for_close_bdouble_red_head()		#大双头大阳线
#	    self.test_for_close_sdouble_red_head()              #小双头大阳线
	    self.test_for_close_vol()				#大阳后缩量

    #大阴收盘翻红
    def test_for_close_green_rt(self):
	hit_indexs = []
        for index in range(0, len(self.hist_days)):
	    cur_stock_day = self.hist_days[index]
            model_close = ModelCloseGreenRT({self.symbol : self.hist_days[index:]}, cur_stock_day.day)

            if model_close.match(cur_stock_day):
#		cur_day = TimeUtils.timestamp2datestring(self.hist_days[index].day)
#		print self.symbol + '-' + cur_day

                hit_indexs.append(index)
                index += 1
        FileUtils.output_backup_test(self.symbol, 'ModelCloseGreenT', self.hist_days, hit_indexs, self.test_days)


    #吊脚阳线
    def test_for_close_t(self):
        hit_indexs = []
        for index in range(0, len(self.hist_days)):
            cur_stock_day = self.hist_days[index]
            model_close = ModelCloseT({self.symbol : self.hist_days[index:]}, cur_stock_day.day)

            if model_close.match(cur_stock_day):
		hit_indexs.append(index)
                index += 1
        FileUtils.output_backup_test(self.symbol, 'ModelCloseT', self.hist_days, hit_indexs, self.test_days)


    #大双头大阳线
    def test_for_close_bdouble_red_head(self):
        hit_indexs = []
        for index in range(0, len(self.hist_days)):
            cur_stock_day = self.hist_days[index]
            model_close = ModelCloseBRedHead({self.symbol : self.hist_days[index:]}, cur_stock_day.day)

            if model_close.match(cur_stock_day):
                hit_indexs.append(index)
                index += 1
        FileUtils.output_backup_test(self.symbol, 'ModelCloseBDoubleRedHead', self.hist_days, hit_indexs, self.test_days)


    #小双头大阳线
    def test_for_close_sdouble_red_head(self):
        hit_indexs = []
        for index in range(0, len(self.hist_days)):
            cur_stock_day = self.hist_days[index]
            model_close = ModelCloseSRedHead({self.symbol : self.hist_days[index:]}, cur_stock_day.day)

            if model_close.match(cur_stock_day):
                hit_indexs.append(index)
                index += 1
        FileUtils.output_backup_test(self.symbol, 'ModelCloseSDoubleRedHead', self.hist_days, hit_indexs, self.test_days)


    #大阳后缩量
    def test_for_close_vol(self):
        hit_indexs = []
        for index in range(0, len(self.hist_days)):
            cur_stock_day = self.hist_days[index]
            model_close = ModelVol({self.symbol : self.hist_days[index:]}, cur_stock_day.day)

            if model_close.match(cur_stock_day):
                hit_indexs.append(index)
                index += 1
        FileUtils.output_backup_test(self.symbol, 'ModelVol', self.hist_days, hit_indexs, self.test_days)

    def test_match(self, symbol, day):
	print 'CloseTest : test_match'


