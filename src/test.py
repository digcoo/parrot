from utils.SystemConfig import *
from dbs.GeodeClient import *

system_config = SystemConfig.get_instance()


print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.SPIDER_PROCESSOR_NUM)

print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.REDIS_SERVER_IP)

print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.REDIS_SERVER_PORT)

print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.GEODE_SERVER_IP)


print jsonpickle.encode(GeodeClient.get_instance().query_stocks_by_ids(['sh601111', 'sh601101', 'sh600111']))

print jsonpickle.encode(GeodeClient.get_instance().query_stocks_by_ids(['sh601111']))
