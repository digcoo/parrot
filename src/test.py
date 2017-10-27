from utils.SystemConfig import *


system_config = SystemConfig.get_instance()


print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.SPIDER_PROCESSOR_NUM)

print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.REDIS_SERVER_IP)

print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.REDIS_SERVER_PORT)

print SystemConfig.get_instance().get(SystemConfig.PROJECT_SYMBOL, SystemConfig.GEODE_SERVER_IP)
