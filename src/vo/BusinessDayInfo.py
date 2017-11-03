#encoding=utf-8

class BusinessDayInfo:

    def __init__(self):
	self.id = ''
	self.b_symbol = ''		#营业部代码
	self.b_name = ''		#营业部
	self.sell_money = 0.0	#买入额(万元)
	self.buy_money = 0.0	#卖出额(万元)
	self.day = None	#交易日期
	self.s_symbol = ''	#股票代码
	self.s_name = ''	#股票名称
