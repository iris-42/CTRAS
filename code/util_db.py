#-*- coding:utf-8 -*-
import MySQLdb

# ---------------------------------------------------------------------------------------
# Description   : Database Processor
# ---------------------------------------------------------------------------------------

class Cluster:
	cluster_id = None
	reports = []

	def __init__(self, cluster_id, reports):
		self.clsuter_id = cluster_id
		self.reports = reports

	def __eq__(self, another):
		if self.clsuter_id == another.get_cluster_id():
			return True
		return False

	def get_cluster_id(self):
		return self.clsuter_id

	def get_reports(self):
		return set(self.reports)

def connect_db():
	db = MySQLdb.connect(host = '',
						user = '',
						passwd = '',
						charset = 'utf8',
						db = ''
						)
	return db

def close_db(db):
	db.close()

def insert_diff_sentence_into_sql(app, duplicate_tag, diff_sentence, diff_sentence_index, report_id):
	db = connect_db()
	cur = db.cursor()
	sql = "INSERT INTO diff_txt VALUES (%s,%s,%s,%s,%s)"
	l = (app, duplicate_tag, diff_sentence, diff_sentence_index, report_id)
	cur.execute(sql, l)
	db.commit()
	close_db(db)

def insert_diff_img_into_sql(app, duplicate_tag, diff_img, report_id):
	db = connect_db()
	cur = db.cursor()
	sql = "INSERT INTO diff_img VALUES (%s,%s,%s,%s)"
	l = (app, duplicate_tag, diff_img, report_id)
	cur.execute(sql, l)
	db.commit()
	close_db(db)

def get_all_sentence_records(app, tag):
	db = connect_db()
	cur = db.cursor()

	cur.execute("SELECT app, duplicate_tag, diff_sentence, " + 
		"diff_sentence_index, report_id FROM diff_txt " +
		"WHERE app = '" + app + "' AND duplicate_tag = " + tag)
	all_records = cur.fetchall()

	close_db(db)
	return all_records

def get_all_img_records(app, tag):
	db = connect_db()
	cur = db.cursor()

	cur.execute("SELECT app, duplicate_tag, diff_img, " + 
		"report_id FROM diff_img " +
		"WHERE app = '" + app + "' AND duplicate_tag = " + tag)
	all_records = cur.fetchall()

	close_db(db)
	return all_records

def get_all_clusters(app, tag, table):
	all_clusters = []

	db = connect_db()
	cur = db.cursor()

	# get all cluster_id
	cur.execute("SELECT DISTINCT cluster_id FROM " + table + 
		" WHERE app = '" + app + "' AND duplicate_tag = " + tag +
		" ORDER BY cluster_id ASC")
	results = cur.fetchall()

	for record in results:
		cluster_id = record[0]
		# get all reports of this cluster
		cur.execute("SELECT DISTINCT report_id FROM " + table +
			" WHERE app = '" + app + "' AND duplicate_tag = " + tag +
			" AND cluster_id = " + str(cluster_id) +
			" ORDER BY report_id ASC")
		reports = [x[0] for x in cur.fetchall()]

		cluster_obj = Cluster(cluster_id, reports)
		all_clusters.append(cluster_obj)

	close_db(db)
	return all_clusters

def select_cluster_combine_tag(group_id, app):#str,int,str,int,int
	db = connect_db()
	cur = db.cursor()
	sql = "SELECT DISTINCT cluster_tag FROM cluster_combine WHERE duplicate_tag = " + str(group_id) + " AND app = '" + app + "' ORDER BY cluster_tag"
	cur.execute(sql)
	records = cur.fetchall()
	close_db(db)
	return records

def select_cluster_id_txt(cluster_combine_tag, group_id, app):#str,int,str,int,int
	db = connect_db()
	cur = db.cursor()
	sql = "SELECT DISTINCT cluster_id_txt FROM cluster_combine WHERE cluster_tag = " + str(cluster_combine_tag) + " AND duplicate_tag = "+ str(group_id) + " AND app = '" + app + "' ORDER BY cluster_id_txt"
	cur.execute(sql)
	records = cur.fetchall()
	close_db(db)
	return records

def select_cluster_id_img(cluster_combine_tag, group_id, app):#str,int,str,int,int
	db = connect_db()
	cur = db.cursor()
	sql = "SELECT DISTINCT cluster_id_img FROM cluster_combine WHERE cluster_tag = " + str(cluster_combine_tag) + " AND duplicate_tag = "+ str(group_id) + " AND app = '" + app + "' ORDER BY cluster_id_img"
	cur.execute(sql)
	records = cur.fetchall()
	close_db(db)
	return records

def select_cluster_txt_tag(cluster_id, group_id, app):#str,int,str,int,int
	db = connect_db()
	cur = db.cursor()
	sql = "SELECT DISTINCT diff_sentence, report_id, diff_sentence_index FROM cluster_txt WHERE cluster_id = " + str(cluster_id) + " AND duplicate_tag = "+ str(group_id) + " AND app = '" + app + "' ORDER BY report_id"
	cur.execute(sql)
	records = cur.fetchall()
	close_db(db)
	return records

def select_cluster_img_tag(cluster_id, group_id, app):
	db = connect_db()
	cur = db.cursor()
	sql = "SELECT DISTINCT diff_img, report_id FROM cluster_img WHERE cluster_id = " + str(cluster_id) + " AND duplicate_tag = "+ str(group_id) + " AND app = '" + app + "' ORDER BY report_id"
	cur.execute(sql)
	records = cur.fetchall()
	close_db(db)
	return records

def insert_top_txt_into_sql(app, duplicate_tag, cluster_tag, txts):#str,int,int,str
	db = connect_db()
	cur = db.cursor()
	sql = "INSERT INTO top_txt VALUES (%s, %s, %s, %s)"
	l = (app, duplicate_tag, cluster_tag, txts)
	cur.execute(sql,l)
	db.commit()
	close_db(db)

def insert_top_img_into_sql(app, duplicate_tag, cluster_tag, imgs):#str,int,int,str
	db = connect_db()
	cur = db.cursor()
	sql = "INSERT INTO top_img VALUES (%s, %s, %s, %s)"
	l = (app, duplicate_tag, cluster_tag, imgs)
	cur.execute(sql,l)
	db.commit()
	close_db(db)