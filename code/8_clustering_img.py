#-*- coding:utf-8 -*-
import os
import traceback
from scipy.spatial import distance
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd

from variables import APPS
from variables import DUPLICATES_CLUSTER_IMG_PATH
from variables import img_similar_threshold

from util_db import connect_db, close_db, get_all_img_records
from util_hist import read_hist_img, get_hist_img_by_img_name

# ---------------------------------------------------------------------------------------
# Description   : Function to aggregate image difference item candidates into candidate clusters
# ---------------------------------------------------------------------------------------

def distance_euclidean_img(app, hist_img, img_i, img_j):
	hist_i = get_hist_img_by_img_name(app, hist_img, img_i)
	hist_j = get_hist_img_by_img_name(app, hist_img, img_j)

	return distance.euclidean(hist_i, hist_j)

def calculate_distance_matrix(app, all_imgs):
	hist_img = read_hist_img(app)
	distance_matrix = [([0] * len(all_imgs)) for i in range(len(all_imgs))]
	for i in range(len(all_imgs)):
		for j in range(len(all_imgs)):
			img_i = all_imgs[i]
			img_j = all_imgs[j]
			distance_matrix[i][j] = distance_euclidean_img(app, hist_img, img_i, img_j)
	return distance_matrix

def clustering_img(app, tag):
	all_records = get_all_img_records(app, tag)
	all_imgs = [x[2] for x in all_records]

	if len(all_records) == 0: # there is no difference item candidate
		return
	elif len(all_records) == 1: # there is only one difference item candidate
		clusters = [1]
	else:
		distance_matrix = calculate_distance_matrix(app, all_imgs)
		distArray = ssd.squareform(distance_matrix)

		Z = sch.linkage(distArray, method = 'single')
		clusters = sch.fcluster(Z, img_similar_threshold, criterion = 'distance')

	# save result to database
	db = connect_db()
	cur = db.cursor()
	for i, cluster_id in enumerate(clusters):
		record = list(all_records[i]) + [int(''.join(['200',str(cluster_id)]))] # # txt: 100xxx, img: 200xxx

		sql = "INSERT INTO cluster_img " + \
			"(app, duplicate_tag, diff_img, report_id, " + \
			"cluster_id) VALUES (%s, %s, %s, %s, %s)"

		try:
			cur.execute(sql, record)
			db.commit()
		except Exception as e:
			traceback.print_exc()
	close_db(db)

for app in APPS:
	for tag in os.listdir('/'.join([DUPLICATES_CLUSTER_IMG_PATH, app])):
		clustering_img(app, tag)