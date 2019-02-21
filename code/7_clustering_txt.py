#-*- coding:utf-8 -*-
import os
import traceback
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd

from variables import POS_TAGS, APPS
from variables import DUPLICATES_CLUSTER_PATH
from variables import T_THRESHOLD

from util_db import connect_db, close_db, get_all_sentence_records
from util_hist import parse_words

# ---------------------------------------------------------------------------------------
# Description   : Function to aggregate textual difference item candidates into candidate clusters
# ---------------------------------------------------------------------------------------

def distance_jaccard_txt(sent_i, sent_j):
	words_i = set(parse_words(sent_i))
	words_j = set(parse_words(sent_j))

	inter = len(words_i & words_j)
	union = len(words_i | words_j)

	if union == 0:
		return 1.0
	return 1.0 - (inter*1.0)/(union*1.0)

def calculate_distance_matrix(all_sentences):
	distance_matrix = [([0] * len(all_sentences)) for i in range(len(all_sentences))]
	for i in range(len(all_sentences)):
		for j in range(len(all_sentences)):
			sent_i = all_sentences[i]
			sent_j = all_sentences[j]
			distance_matrix[i][j] = distance_jaccard_txt(sent_i, sent_j)
	return distance_matrix

def clustering_txt(app, tag):
	all_records = get_all_sentence_records(app, tag)
	all_sentences = [x[2] for x in all_records]

	if len(all_records) == 0: # there is no difference item candidate
		return
	elif len(all_records) == 1: # there is only one difference item candidate
		clusters = [1]
	else:
		distance_matrix = calculate_distance_matrix(all_sentences)
		distArray = ssd.squareform(distance_matrix)

		Z = sch.linkage(distArray, method = 'single')
		clusters = sch.fcluster(Z, T_THRESHOLD, criterion = 'distance')

	# save result to database
	db = connect_db()
	cur = db.cursor()
	for i, cluster_id in enumerate(clusters):
		record = list(all_records[i]) + [int(''.join(['100',str(cluster_id)]))] # txt: 100xxx, img: 200xxx

		sql = "INSERT INTO cluster_txt " + \
			"(app, duplicate_tag, diff_sentence, diff_sentence_index, report_id, cluster_id) " + \
			"VALUES (%s, %s, %s, %s, %s, %s)"

		try:
			cur.execute(sql, record)
			db.commit()
		except Exception as e:
			traceback.print_exc()
	close_db(db)

for app in APPS:
	for tag in os.listdir('/'.join([DUPLICATES_CLUSTER_PATH, app])):
		clustering_txt(app, tag)