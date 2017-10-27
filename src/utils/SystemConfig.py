#encoding=utf-8

import traceback
import os
import jsonpickle
import ConfigParser

class SystemConfig:

    #project
    PROJECT_SYMBOL = 'parrot'


    #geode
    GEODE_SERVER_IP = 'geode.server.ip'
    GEODE_SERVER_PORT = 'geode.server.port'

    #redis
    REDIS_SERVER_IP = 'redis.server.ip'
    REDIS_SERVER_PORT = 'redis.server.port'

    #spider
    SPIDER_SYMBOL_STUB_START = 'spider.symbol.stub.start'
    SPIDER_SYMBOL_STUB_END = 'spider.symbol.stub.end'
    SPIDER_SYMBOL_NUM_PER_PROCESSOR = 'spider.symbol.num.per.processor'
    SPIDER_BATCH_NO = 'spider.batch.no'
    SPIDER_PROCESSOR_NUM = 'spider.processor.num'
    

    __instance = None

    __config = None

    @staticmethod
    def get_instance():
	if SystemConfig.__instance == None:
	    SystemConfig.__instance = SystemConfig()
	return SystemConfig.__instance


    def __init__(self):
	try:
	    conf_dir_path = os.path.dirname(os.getcwd())
	    conf_dir_path = os.path.dirname(conf_dir_path)
	    conf_path = conf_dir_path + "/conf/parrot.conf"
	    self.__config = ConfigParser.ConfigParser()
	    self.__config.read(conf_path)
	except Exception, e:
	    traceback.print_exc()

    def get(self, section, key):
	try:
	    return self.__config.get(section, key)
	except Exception, e:
	    return None
