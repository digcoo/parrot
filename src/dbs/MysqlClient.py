import pymysql.cursors
import datetime
import time
import traceback

class MysqlClient:

    __instance = None

    @staticmethod
    def get_instance():
        if MysqlClient.__instance is None:
            MysqlClient.__instance = MysqlClient()
        return MysqlClient.__instance

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
            traceback.print_exc()

    def close(self):
	try:
#	    self.connection.close()
	    print ''
	except Exception, e:
	    traceback.print_exc()


    def query_stock_hit_by_symbol_day(self, symbol, day):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT `id`, `symbol`, `buy_time`, `buy_price`, `hit_model`, 'day', `sell_time`,`sell_price`,`status` FROM `stock_pool` where `day` = %s and `symbol` = %s"
                cursor.execute(sql, (day, symbol, ))
                return cursor.fetchall()
        except Exception, e:
            traceback.print_exc()
        finally:
            self.close()



    def query_stock_hit_page_list(self, symbol, status, model, page):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT `id`, `symbol`, `buy_time`, `buy_price`, `hit_model`, `day`, `sell_time`,`sell_price`,`status`  FROM `stock_pool` where 1 = 1 "
		if symbol is not None and len(symbol.strip()) > 0:
		    sql = sql + " and `symbol` like '%" + symbol.strip() + "%'"
                if model is not None and len(model.strip()) > 0:
                    sql = sql + " and `hit_model` like '%" + model.strip() + "%'"
                if status is not None and len(status.strip()) > 0:
                    sql = sql + " and `status` = '" + status.strip() + "'"

		sql = sql + " and `day` = "
		day_sql = "(SELECT distinct(`day`) from `stock_pool` group by `day` order by `day` desc limit " + str((page-1)) + ",1)"
		sql = sql + day_sql + " order by `buy_time` desc "

                cursor.execute(sql)
                return cursor.fetchall()
        except Exception, e:
            traceback.print_exc()
	finally:
	    self.close()

    def query_stock_hit_page_count(self):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT COUNT(DISTINCT(t.`day`)) as day_count from `stock_pool` t"
                cursor.execute(sql)
                return cursor.fetchone()['day_count']
        except Exception, e:
            traceback.print_exc()
        finally:
            self.close()



    def add_stock_hit(self, stock_hit):
        try:
            local_stock_hit = self.query_stock_hit_by_symbol_day(stock_hit.symbol, stock_hit.day)
	    if local_stock_hit == None or len(local_stock_hit) == 0:
		self.conn()
                with self.connection.cursor() as cursor:
                    sql = "INSERT INTO `stock_pool` (`symbol`, `buy_time`, `buy_price`, `hit_model`, `day`, `status`) values(%s, %s, %s, %s, %s, %s)"
		    cursor.execute(sql, (stock_hit.symbol, stock_hit.buy_time, stock_hit.buy_price, stock_hit.hit_model, stock_hit.day, stock_hit.status ))
                    self.connection.commit()

        except Exception, e:    
	    traceback.print_exc()
	finally:
	    self.close()


    def del_stock_hit(self, id):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "DELETE FROM `stock_pool` where `id` = %s"
                cursor.execute(sql, (id,))
                self.connection.commit()

        except Exception, e:
            traceback.print_exc()
        finally:
            self.close()


    def sell_stock_hit(self, id, sell_time, sell_price):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "UPDATE `stock_pool`  SET `sell_time` = %s, `sell_price` = %s, `status` = 'sold' where `id` = %s"
                cursor.execute(sql, (sell_time, sell_price, id ))
                self.connection.commit()

        except Exception, e:
            traceback.print_exc()
        finally:
            self.close()


#//////////////////////////////////////////////////////////////////plate/////////////////////////////////////////////////////////////////////////

    def query_all_plates(self):
        try:
            self.conn()
            with self.connection.cursor() as cursor:
                sql = "SELECT `id`,`symbol`, `name`, `category` from `plate` "
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception, e:
            traceback.print_exc()
        return None



    def query_plates_by_ids(self, ids):
	try:
	    id_str = StringUtils.parse_list_to_idstr(ids)
	    if id_str is not None and len(id_str) > 0:
		self.conn()
		with self.connection.cursor() as cursor:
		    sql = "SELECT `id`,`symbol`, `name`, `category` from `plate` where `id` in (%s) " % (id_str, )
                    cursor.execute(sql)
                    return cursor.fetchall()
	except Exception, e:
	    traceback.print_exc()
	return None

    def add_batch_plates(self, plates):
        try:
	    for plate in plates:
		local_plates = self.query_plates_by_ids([plate.id])
		if local_plates == None or len(local_plates) == 0:
		    self.conn()
		    with self.connection.cursor() as cursor:
			sql = "INSERT INTO `plate` (`id`, `symbol`, `name`, `category`) values(%s, %s, %s, %s)"
			cursor.execute(sql, (plate.id, plate.symbol, plate.name, plate.category))
			self.connection.commit()
		else:
                    self.conn()
                    with self.connection.cursor() as cursor:
                        sql = "UPDATE `plate` set `symbol` = %s, `name` = %s, `category` = %s where `id` = %s"
                        cursor.execute(sql, (plate.symbol, plate.name, plate.category, plate.id))
                        self.connection.commit()

        except Exception, e:
            traceback.print_exc()
        finally:
            self.close()

#//////////////////////////////////////////////////////////////////plate/////////////////////////////////////////////////////////////////////////



#//////////////////////////////////////////////////////////////////rel_plate_stock/////////////////////////////////////////////////////////////////////////
    def query_rel_plate_stock_by_ids(self, ids):
        try:
            id_str = StringUtils.parse_list_to_idstr(ids)
            if id_str is not None and len(id_str) > 0:
                self.conn()
                with self.connection.cursor() as cursor:
                    sql = "SELECT `id`, `plate_name`, `plate_symbol`, `stock_symbol`, `stock_name` from `rel_plate_stock` where `id` in (%s) " % (id_str, )
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception, e:
            traceback.print_exc()
        return None

    def add_batch_rel_plate_stocks(self, rel_plate_stocks):
        try:
            for rel in rel_plate_stocks:
                local_rels = self.query_rel_plate_stock_by_ids([rel.id])
                if local_rels == None or len(local_rels) == 0:
                    self.conn()
                    with self.connection.cursor() as cursor:
                        sql = "INSERT INTO `rel_plate_stock` (`id`, `plate_name`, `plate_symbol`, `stock_symbol`, `stock_name`) values(%s, %s, %s, %s, %s)"
                        cursor.execute(sql, (rel.id, rel.plate_name, rel.plate_code, rel.stock_symbol, rel.stock_name))
                        self.connection.commit()
                else:
                    self.conn()
                    with self.connection.cursor() as cursor:
                        sql = "UPDATE `rel_plate_stock` set `plate_name` = %s, `plate_symbol` = %s, `stock_symbol` = %s, `stock_name` = %s where `id` = %s"
                        cursor.execute(sql, (rel.plate_name, rel.plate_code, rel.stock_symbol, rel.stock_name, rel.id))
                        self.connection.commit()

        except Exception, e:
            traceback.print_exc()
        finally:
            self.close()

#//////////////////////////////////////////////////////////////////rel_plate_stock/////////////////////////////////////////////////////////////////////////


