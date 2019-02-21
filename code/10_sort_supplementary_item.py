#-*- coding:utf-8 -*-
import os
import numpy as np
from scipy.spatial import distance

from variables import POS_TAGS, APPS
from variables import DUPLICATES_CLUSTER_PATH, DUPLICATES_CLUSTER_IMG_PATH

from util_db import select_cluster_combine_tag
from util_db import select_cluster_id_txt, select_cluster_id_img
from util_db import select_cluster_txt_tag, select_cluster_img_tag
from util_db import insert_top_txt_into_sql, insert_top_img_into_sql
from util_hist import read_hist_img, get_img_pos
from util_hist import preprocess_line
from util_pagerank import graphMove, firstPr, pageRank

# ---------------------------------------------------------------------------------------
# Description   : Function to sort the sentences/screenshots within each supplementary and save them to database
# ---------------------------------------------------------------------------------------

def distance_sentence_jaccard(sentence_a,sentence_b):
	inter = 0
	union = 0
	for word_a in sentence_a:
		if word_a in sentence_b:
				inter = inter + 1
	union = len(sentence_a) + len(sentence_b) - inter
	return 1 - (inter*1.0)/(union*1.0)

def distance_img(app,img_name_a,img_name_b):
	hist_img = read_hist_img(app)

	index_a = get_img_pos(img_name_a)
	index_b = get_img_pos(img_name_b)

	img_a = hist_img[index_a]
	img_b = hist_img[index_b]

	dis = distance.euclidean(img_a, img_b)
	return dis

def processing(sentence_list):
	line_list = []
	for line in sentence_list:
		if line == '':
			break
		line = preprocess_line(line)
		words = [x.split('_') for x in line.split(' ')]
		line_list.append(words)
	return line_list

def calculate_txt_pr_matrix(diff_sentence_list):
	pr_matrix = []
	for sentence_a in diff_sentence_list:
		weight_list = []
		for sentence_b in diff_sentence_list:
			distance = distance_sentence_jaccard(sentence_a, sentence_b)
			weight = 1 - distance
			weight_list.append(weight)
			distance = 0
			weight = 0
		pr_matrix.append(weight_list)
		
	return pr_matrix

def calculate_img_pr_matrix(app,diff_img_list):
	pr_matrix = []
	for img_a in diff_img_list:
		weight_list = []
		for img_b in diff_img_list:
			distance = distance_img(app, img_a, img_b)

			weight = 1 - distance
			weight_list.append(weight)
			distance = 0
			weight = 0
		pr_matrix.append(weight_list)
		
	return pr_matrix

def get_txt_pagerank(diff_sentence_list):
	pr_matrix = calculate_txt_pr_matrix(diff_sentence_list)
	
	a_matrix = np.array(pr_matrix)
	M = graphMove(a_matrix)
	pr = firstPr(M)  
	p = 0.8  
	re = pageRank(p,M,pr) 
	return re

def get_img_pagerank(diff_img_list):
	pr_matrix = calculate_img_pr_matrix(app, diff_img_list)
	a_matrix = np.array(pr_matrix)
	M = graphMove(a_matrix)
	pr = firstPr(M)  
	p = 0.8  
	re = pageRank(p,M,pr)        
	return re

def calculate_cluster_txt_pr(app):
	for group_id in sorted(os.listdir('/'.join([DUPLICATES_CLUSTER_PATH, app]))):
		cluster_combine_tags = select_cluster_combine_tag(group_id, app)
		for cluster_combine_tag in cluster_combine_tags:
			cluster_ids = select_cluster_id_txt(cluster_combine_tag[0], group_id, app)
			for cluster_id_ in cluster_ids:
				cluster_id = cluster_id_[0]
				if cluster_id != None: # contain textual candidate cluster
					cluster_txt = select_cluster_txt_tag(cluster_id, group_id, app)
					diff_sentence_list = []
					report_id_list = []
					diff_sentence_index_list = []
					for cluster_info in cluster_txt:
						diff_sentence_list.append(cluster_info[0])
						report_id_list.append(cluster_info[1])
						diff_sentence_index_list.append(cluster_info[2])
					if len(diff_sentence_list) > 1:
						diff_sentence_list_process = processing(diff_sentence_list)
						pr = get_txt_pagerank(diff_sentence_list_process)
						pr_dict = {}
						flag1 = 0
						for tmp in pr:
							pr_dict[str(flag1)] = tmp[0]
							flag1 = flag1 + 1
						top_n = 0
						for key,value in sorted(pr_dict.iteritems(), key=lambda d:d[1], reverse = True):
							txts = (str(top_n), diff_sentence_list[int(key)], report_id_list[int(key)], diff_sentence_index_list[int(key)])
							insert_top_txt_into_sql(app, group_id, cluster_combine_tag[0], txts)
							top_n = top_n + 1
					if len(diff_sentence_list) == 1: # there is only one sentence
						txts = ('0', diff_sentence_list[0], report_id_list[0], diff_sentence_index_list[0])
						insert_top_txt_into_sql(app, group_id, cluster_combine_tag[0], txts)

def calculate_cluster_img_pr(app):
	for group_id in sorted(os.listdir('/'.join([DUPLICATES_CLUSTER_IMG_PATH, app]))):
		cluster_combine_tags = select_cluster_combine_tag(group_id, app)
		for cluster_combine_tag in cluster_combine_tags:
			cluster_ids = select_cluster_id_img(cluster_combine_tag[0], group_id,app)
			for cluster_id_ in cluster_ids:
				cluster_id = cluster_id_[0]
				if cluster_id != None: # contain image candidate cluster
					cluster_img = select_cluster_img_tag(cluster_id, group_id, app)
					diff_img_list = []
					report_id_list = []
					for cluster_info in cluster_img:
						diff_img_list.append(cluster_info[0])
						report_id_list.append(cluster_info[1])
					if len(diff_img_list) > 1:
						pr = get_img_pagerank(diff_img_list)
						pr_dict = {}
						flag1 = 0
						for tmp in pr:
							pr_dict[str(flag1)] = tmp[0]
							flag1 = flag1 + 1
						top_n = 0
						for key,value in sorted(pr_dict.iteritems(), key=lambda d:d[1], reverse = True):
							imgs = []
							imgs = (str(top_n), diff_img_list[int(key)], report_id_list[int(key)])
							insert_top_img_into_sql(app,group_id,cluster_combine_tag[0],imgs)
							top_n = top_n + 1
					if len(diff_img_list) == 1: # there is only one image
						imgs = ('0', diff_img_list[0], report_id_list[0])
						insert_top_img_into_sql(app,group_id,cluster_combine_tag[0],imgs)

for app in APPS:
	calculate_cluster_txt_pr(app)
	calculate_cluster_img_pr(app)