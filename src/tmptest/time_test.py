import datetime
import time

start = int(time.mktime(datetime.datetime.now().timetuple()))

time.sleep(5)

end = int(time.mktime(datetime.datetime.now().timetuple()))

print str(end - start)
