import os

from sys import path

path.append(os.getcwd() + '/vo')

from StockInfo import *

stock_info = StockInfo()
stock_info.id = '312'
