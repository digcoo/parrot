#encoding=utf-8
import time
import datetime
import calendar

class TimeUtils:

    DATE_FORMAT_YYYYMMDD = '%Y%m%d'
    TIME_FORMAT_YYYYMMDDHHMM = '%Y%m%d%H%M'
    TIME_FORMAT_YYYYMMDDHHMMSS = '%Y%m%d%H%M%S'
    TIME_FORMAT_HHMMSS= '%H%M%S'

    @staticmethod
    def timestamp2datestring(timestamp):
	dt = time.localtime(timestamp)
	return time.strftime('%Y-%m-%d',dt)


    @staticmethod
    def timestamp2timestring(timestamp):
	dt = time.localtime(timestamp)
	return time.strftime('%Y-%m-%d %H:%M:%S',dt)


    @staticmethod
    def datestring2timestamp(datestring):
	return int(time.mktime(time.strptime(datestring, "%Y-%m-%d")))

	
    @staticmethod
    def datestring2datestamp(datestring, format):
	return int(time.mktime(time.strptime(datestring, format)))

    @staticmethod
    def datestamp2datestring(datestamp, format):
	dt = time.localtime(datestamp)
        return time.strftime(format,dt)


    @staticmethod
    def timestring2timestamp(timestring):
        return int(time.mktime(time.strptime(timestring, "%Y-%m-%d %H:%M:%S")))

    @staticmethod
    def get_current_timestamp():
	return int(time.mktime(datetime.datetime.now().timetuple()))

    @staticmethod
    def get_current_datestamp():
	datestring = TimeUtils.timestamp2datestring(TimeUtils.get_current_timestamp())
	return TimeUtils.datestring2timestamp(datestring)

    @staticmethod
    def get_current_datestring():
        return TimeUtils.timestamp2datestring(TimeUtils.get_current_timestamp())

    @staticmethod
    def get_current_timestring():
        return TimeUtils.timestamp2timestring(TimeUtils.get_current_timestamp())


    @staticmethod
    def is_after(timestring):
	current_time = TimeUtils.get_current_timestamp()
	current_datestring = TimeUtils.get_current_datestring()
	source_time = int(time.mktime(time.strptime(current_datestring + ' ' + timestring, "%Y-%m-%d %H:%M:%S")))
	return source_time < current_time
   
    @staticmethod
    def date_diff(timestamp_start, timestamp_end):
	return abs(timestamp_end - timestamp_start) / (3600 * 24)

    @staticmethod
    def date_add(timestamp_start, intv):
	return timestamp_start + (intv * 3600 * 24)

    @staticmethod
    def is_same_week_with_datestamp(datestamp1, datestamp2):
	date1_obj = datetime.datetime.fromtimestamp(datestamp1)
	date2_obj = datetime.datetime.fromtimestamp(datestamp2)
	return date1_obj.year == date2_obj.year and date1_obj.month == date2_obj.month and TimeUtils.week_of_month_from_datestamp(datestamp1) == TimeUtils.week_of_month_from_datestamp(datestamp2)

    @staticmethod
    def is_same_month_with_datestamp(datestamp1, datestamp2):
        date1_obj = datetime.datetime.fromtimestamp(datestamp1)
        date2_obj = datetime.datetime.fromtimestamp(datestamp2)
	return date1_obj.year == date2_obj.year and date1_obj.month == date2_obj.month


    @staticmethod
    def day_of_week_from_datestamp(datestamp):
	date_obj = datetime.datetime.fromtimestamp(datestamp)
	return date_obj.isoweekday()

    @staticmethod
    def year_from_datestamp(datestamp):
        date_obj = datetime.datetime.fromtimestamp(datestamp)
        return date_obj.year

    @staticmethod
    def month_from_datestamp(datestamp):
	date_obj = datetime.datetime.fromtimestamp(datestamp)
	return date_obj.month

    @staticmethod
    def minute_from_timestamp(timestamp):
	time_obj = datetime.datetime.fromtimestamp(timestamp)
        return time_obj.minute

    @staticmethod
    def week_of_month_from_datestamp(datestamp):
	date_obj = datetime.datetime.fromtimestamp(datestamp)
	year = date_obj.year
	month = date_obj.month
	day = date_obj.day
	
	date_start = datetime.datetime.fromtimestamp(TimeUtils.datestring2timestamp(str(year) + '-' + str(month) + '-' + '01'))
	date_start_weekday = date_start.isoweekday()
	return (day -1 + date_start_weekday - 1) / 7 + 1

    @staticmethod
    def lastday_of_month(year, month):
	first_weekday, month_total_days = calendar.monthrange(year, month)	#当月第一天星期几，当月总天数
	lastday = datetime.date(year=year, month=month, day=month_total_days)
	return int(time.mktime(lastday.timetuple()))

    @staticmethod
    def lastday_of_month_from_datestamp(datestamp):
	current_year = TimeUtils.year_from_datestamp(datestamp)
        current_month = TimeUtils.month_from_datestamp(datestamp)
	return TimeUtils.lastday_of_month(current_year, current_month)

    @staticmethod
    def current_friday_from_datestamp(datestamp):
        current_weekday = TimeUtils.day_of_week_from_datestamp(datestamp)
        current_friday_datestamp = TimeUtils.date_add(TimeUtils.get_current_datestamp(), 5 - current_weekday)
	return current_friday_datestamp

    @staticmethod
    def count_days_of_month_from_datestamp(datestamp):
        current_year = TimeUtils.year_from_datestamp(datestamp)
        current_month = TimeUtils.month_from_datestamp(datestamp)
	first_weekday, month_total_days = calendar.monthrange(year, month)      #当月第一天星期几，当月总天数
	return month_total_days

    @staticmethod
    def is_lastday_of_month_from_datestamp(datestamp):
	current_year = TimeUtils.year_from_datestamp(datestamp)
	current_month = TimeUtils.month_from_datestamp(datestamp)
	first_weekday, month_total_days = calendar.monthrange(current_year, current_month)
	date_obj = datetime.datetime.fromtimestamp(datestamp)
	return date_obj.day == month_total_days

    @staticmethod
    def day_of_month_from_datestamp(datestamp):
	date_obj = datetime.datetime.fromtimestamp(datestamp)
	return date_obj.day


if __name__ == '__main__':
#    datestring = TimeUtils.timestamp2datestring(TimeUtils.get_current_timestamp())
#    print TimeUtils.datestring2timestamp(datestring)

#    print TimeUtils.week_of_month_from_datestamp(TimeUtils.get_current_datestamp())
#    print TimeUtils.compare_current('10:40:30')
#    print TimeUtils.get_current_datestamp()

#    print TimeUtils.lastday_of_month(2017, 9)
#    print TimeUtils.is_lastday_of_month_from_datestamp(TimeUtils.get_current_datestamp())

     print TimeUtils.minute_from_timestamp(TimeUtils.get_current_timestamp())
