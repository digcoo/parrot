import pymysql.cursors
import datetime
import time

class MysqlConn:

    def __init__(self):
	self.connection = None

    def conn(self):
        try:
            self.connection = pymysql.connect(host='cms-metadata-dev-117.cdslstjgevzs.rds.cn-north-1.amazonaws.com.cn',
                             user='bestv',
                             password='bestvwin',
                             db='stock',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
        except Exception, e:
            print e

    def close(self):
	try:
#	    self.connection.close()
	    print ''
	except Exception, e:
	    print e

    def query_stock_by_symbol(self, symbol):
	try:
	    self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT `id`, `code`, `name`,  `symbol` FROM `stock` WHERE `symbol` = %s"
                cursor.execute(sql, (symbol, ))
                return cursor.fetchone()
	except Exception, e:
	    print e
	finally:
	    self.close()

    def query_stock_day_by_id(self, id):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT `id`, `symbol` FROM `stock_day` WHERE `id` = %s"
                cursor.execute(sql, (id, ))
                return cursor.fetchone()
        except Exception, e:
            print e
        finally:
            self.close()


    def query_stock_page_list(self, page, size):
        try:
	    start = (page -1) * size
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT `id`, `code`, `name`,  `symbol` FROM `stock` limit %s, %s"
                cursor.execute(sql, (start, size, ))
                return cursor.fetchall()
        except Exception, e:
            print e
	finally:
	    self.close()

    def add_stock(self, stock):
        try:
            local_stock = self.query_stock_by_symbol(stock.symbol)
	    if(local_stock == None):
		self.conn()
                with self.connection.cursor() as cursor:
                    sql = "INSERT INTO `stock` (`code`, `name`, `symbol`) VALUES(%s, %s, %s)"
		    cursor.execute(sql, (stock.code, stock.name, stock.symbol, ))
                    self.connection.commit()

	    else:
                self.conn()
                with self.connection.cursor() as cursor:
                    sql = "update `stock` set `name` = %s, `code` = %s where symbol = %s"
                    cursor.execute(sql, (stock.name, stock.code, stock.symbol, ))
                    self.connection.commit()

        except Exception, e:    
	    print e
	finally:
	    self.close()

    def add_stock_day(self, stock):
        try:
	    day = time.strftime('%Y%m%d',time.localtime(time.time()))
	    id = stock.symbol + day
            local_stock_day = self.query_stock_day_by_id(id)
            if(local_stock_day == None):
                self.conn()
                with self.connection.cursor() as cursor:
                    sql = "INSERT INTO `stock_day` (`id`, `symbol`, `high`, `low`, `op`, `close`, `vol`, `money`, `sell1`, `sell1_vol`,`buy1`, `buy1_vol`, `day`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (id, stock.symbol, stock.high, stock.low, stock.op, stock.close, stock.vol, stock.money, stock.sell1, stock.sell1_vol, stock.buy1, stock.buy1_vol, stock.day, ))
                    self.connection.commit()

	    else:
		self.conn()
                with self.connection.cursor() as cursor:
                    sql = "update `stock_day` set `high` = %s, `low` = %s, `op` =%s, `close` = %s, `vol` = %s, `money` = %s, `sell1` = %s, `sell1_vol` = %s,`buy1` = %s, `buy1_vol` = %s, `day` = %s where id = %s"
                    cursor.execute(sql, (stock.high, stock.low, stock.op, stock.close, stock.vol, stock.money, stock.sell1, stock.sell1_vol, stock.buy1, stock.buy1_vol, stock.day, id, ))
                    self.connection.commit()

        except Exception, e:
            print e
        finally:
            self.close()


