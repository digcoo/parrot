#encoding=utf-8

class CommonUtils:
    @staticmethod
    def filter_symbol_dic(symbol_dic):
        final_candidate_stocks = {}
        if symbol_dic is not None:
            for symbol in symbol_dic.keys():
                if(symbol[0 : 3] != 'sz3'):
                    final_candidate_stocks[symbol] = symbol_dic.get(symbol)
        return final_candidate_stocks

    @staticmethod
    def filter_stock(stock):
        if(stock.symbol[0 : 3] != 'sz3'):
	    return stock
        return None


    @staticmethod
    def filter_symbols(symbols):
	ret_symbols = []
	for symbol in symbols:
	    if CommonUtils.filter_symbol(symbol) is not None:
		ret_symbols.append(symbol)
        return ret_symbols


    @staticmethod
    def filter_symbol(symbol):
        if(symbol[0 : 3] != 'sz3'):
            return symbol
        return None
	
