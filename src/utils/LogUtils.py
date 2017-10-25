#encoding=utf-8

import codecs
import jsonpickle as json
from utils.TimeUtils import *

class LogUtils:

    morn_hit_symbols_out_file_path = '/home/ubuntu/scripts/output'

    @staticmethod
    def info(text):
	print TimeUtils.get_current_timestring() + '  ' + text



    @staticmethod
    def hit_to_file(text):
        file_name = 'hit_symbols_' + TimeUtils.get_current_datestring().replace('-', '') + '.txt'
	final_file_name = LogUtils.morn_hit_symbols_out_file_path + '/' + file_name
	update_file = codecs.open(final_file_name, 'w', 'utf-8')
	update_file.write(text)
	update_file.close()


if __name__ == '__main__':
    LogUtils.hit_to_file('test') 
	
	



