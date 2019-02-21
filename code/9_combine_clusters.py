#-*- coding:utf-8 -*-
import os

from variables import APPS
from variables import DUPLICATES_CLUSTER_PATH
from variables import LINK_THRESHOLD

from util_db import connect_db, close_db, get_all_clusters

# ---------------------------------------------------------------------------------------
# Description   : Function to combine candidate clusters
# ---------------------------------------------------------------------------------------

def get_link_between_clusters(txt_cluster, img_cluster):
	txt_reports = txt_cluster.get_reports()
	img_reports = img_cluster.get_reports()

	inter = len(txt_reports & img_reports)
	union = len(txt_reports | img_reports)

	distance = 1 - (1.0*inter)/(1.0*union)

	if distance <= LINK_THRESHOLD:
		return 1
	return 0

def link(all_txt_clusters, all_img_clusters):
	link_matrix = [([0] * len(all_img_clusters)) for i in range(len(all_txt_clusters))]

	for i in range(len(all_txt_clusters)):
		for j in range(len(all_img_clusters)):
			txt_cluster = all_txt_clusters[i]
			img_cluster = all_img_clusters[j]
			link_matrix[i][j] = get_link_between_clusters(txt_cluster, img_cluster)
	return link_matrix

def get_all_linked_img_clusters(link_matrix, i, all_img_clusters):
	indices = [i for i,x in enumerate(link_matrix[i]) if x==1]
	linked_img_clusters = [all_img_clusters[i] for i in indices]
	return linked_img_clusters

def join(app, tag, all_txt_clusters, all_img_clusters, link_matrix):
	db = connect_db()
	cur = db.cursor()

	AUTO_CLUSTER_ID = 0
	linked_img_clusters = set() # just_cluster_id

	for i, txt_cluster in enumerate(all_txt_clusters):
		txt_cluster_id = txt_cluster.get_cluster_id()
		linked_img_clusters_i = get_all_linked_img_clusters(link_matrix, i, all_img_clusters)

		if len(linked_img_clusters_i) == 0: # there is no image candidate cluster that is linked with this cluster
			cur.execute("INSERT INTO cluster_combine (app, duplicate_tag, cluster_tag, "+
				"cluster_id_txt) VALUES (%s, %s, %s, %s)",
				(app, tag, AUTO_CLUSTER_ID, txt_cluster_id))
			db.commit()
			AUTO_CLUSTER_ID += 1

		for img_cluster in linked_img_clusters_i: # save the relationship to database
			img_cluster_id = img_cluster.get_cluster_id()
			cur.execute("INSERT INTO cluster_combine (app, duplicate_tag, cluster_tag, "+
				"cluster_id_txt, cluster_id_img) VALUES (%s, %s, %s, %s, %s)",
				(app, tag, AUTO_CLUSTER_ID, txt_cluster_id, img_cluster_id))
			db.commit()
			AUTO_CLUSTER_ID += 1
			linked_img_clusters.add(img_cluster_id)

	# save rest image candidate clusters to database
	unlinked_img_clusters = set([x.get_cluster_id() for x in all_img_clusters]) - linked_img_clusters
	for img_cluster in unlinked_img_clusters:
		cur.execute("INSERT INTO cluster_combine (app, duplicate_tag, cluster_tag, "+
			"cluster_id_img) VALUES (%s, %s, %s, %s)",
			(app, tag, AUTO_CLUSTER_ID, img_cluster))
		db.commit()
		AUTO_CLUSTER_ID += 1

	close_db(db)

def combine_clusters(app, tag):
	all_txt_clusters = get_all_clusters(app, tag, 'cluster_txt')
	all_img_clusters = get_all_clusters(app, tag, 'cluster_img')

	link_matrix = link(all_txt_clusters, all_img_clusters)

	join(app, tag, all_txt_clusters, all_img_clusters, link_matrix)


for app in APPS:
	for tag in os.listdir('/'.join([DUPLICATES_CLUSTER_PATH, app])):
		combine_clusters(app, tag)