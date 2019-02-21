#-*- coding:utf-8 -*-
import os,csv
import numpy as np
from scipy.spatial import distance
from itertools import combinations, product

from variables import APPS
from variables import DISTANCE_BASE_PATH
from variables import img_similar_threshold, alpha, beta

from util_corpus import get_all_reports
from util_hist import read_hist_txt, read_hist_img, get_hist_txt, get_hist_img

# ---------------------------------------------------------------------------------------
# Description   : Function to calculate distance between reports
# ---------------------------------------------------------------------------------------

def unique_imgset(hist):
	# remove duplicated images from imgset
	rm_tag = [False for x in range(len(hist))]
	for i, j in combinations(range(len(hist)), 2): # i always < j
		if distance.euclidean(hist[i], hist[j]) <= img_similar_threshold:
			rm_tag[j] = True # remove images with larger index
	hist_unique = [hist[i] for i,x in enumerate(rm_tag) if x == False]
	return hist_unique

def distance_txt_jaccard(hist_a, hist_b):
	inter = 0
	union = 0
	for i in range(len(hist_a)):
		if hist_a[i] > 0 and hist_b[i] > 0:
			inter += 1
			union += 1
		elif hist_a[i] > 0 or hist_b[i] > 0:
			union += 1
	if union == 0.0:
		return 1.0
	return 1.0 - (inter*1.0)/(union*1.0)

def distance_imgset_jaccard(hist_a, hist_b):
	# calculate the distance between imgset
	if len(hist_a) == 0 and len(hist_b) == 0:
		return 0.0
	if len(hist_a) == 0 or len(hist_b) == 0:
		return 1.0

	# remove duplicated images in each group
	hist_unique_a = unique_imgset(hist_a)
	hist_unique_b = unique_imgset(hist_b)

	# calculate the inter set and union set between hist_unique_a and hist_unique_b
	hist_tag_a = range(len(hist_unique_a))
	hist_tag_b = [i+len(hist_tag_a) for i in range(len(hist_unique_b))]
	products = list(product(hist_tag_a, hist_tag_b))
	for i, j in products:
		img_a = hist_a[i]
		img_b = hist_b[j-len(hist_tag_a)]
		dis = distance.euclidean(img_a, img_b)
		if dis <= img_similar_threshold:
			if hist_tag_a[i] <= hist_tag_b[j-len(hist_tag_a)]:
				hist_tag_b[j-len(hist_tag_a)] = hist_tag_a[i]
			else:
				hist_tag_a[i] = hist_tag_b[j-len(hist_tag_a)]

	inter = len(set(hist_tag_a).intersection(hist_tag_b))
	union = len(set(hist_tag_a).union(hist_tag_b))
	return 1.0 - (inter*1.0)/(union*1.0)

def distance_report_harmonic(DT, DS, hist_img_a, hist_img_b):
	if DT == 0.0:
		return 0.0
	if DS == 0.0:
		return alpha*DT
	return (1+beta*beta)*(DS*DT)/(beta*beta*DS+DT)

def calculate_distance(app):
	if not os.path.exists('/'.join([DISTANCE_BASE_PATH, app])):
		os.makedirs('/'.join([DISTANCE_BASE_PATH, app]))
	
	all_reports = get_all_reports(app)
	hist_txt = read_hist_txt(app)
	hist_img = read_hist_img(app)

	distance_matrix_txt = [([0] * len(all_reports)) for i in range(len(all_reports))]
	distance_matrix_img = [([0] * len(all_reports)) for i in range(len(all_reports))]
	distance_matrix_report = [([0] * len(all_reports)) for i in range(len(all_reports))]

	for i in range(len(all_reports)):
		for j in range(len(all_reports)):
			report_a = all_reports[i]
			report_b = all_reports[j]

			hist_txt_a = get_hist_txt(app, hist_txt, report_a)
			hist_txt_b = get_hist_txt(app, hist_txt, report_b)

			hist_img_a = get_hist_img(app, hist_img, report_a)
			hist_img_b = get_hist_img(app, hist_img, report_b)

			distance_txt = distance_txt_jaccard(hist_txt_a, hist_txt_b)
			distance_imgset = distance_imgset_jaccard(hist_img_a, hist_img_b)
			distance_report = distance_report_harmonic(distance_txt, distance_imgset, hist_img_a, hist_img_b)

			distance_matrix_txt[i][j] = distance_txt
			distance_matrix_img[i][j] = distance_imgset
			distance_matrix_report[i][j] = distance_report
	
	# save all distance
	np.save('/'.join([DISTANCE_BASE_PATH, app, 'distance_txt.npy']), distance_matrix_txt)
	np.save('/'.join([DISTANCE_BASE_PATH, app, 'distance_img.npy']), distance_matrix_img)
	np.save('/'.join([DISTANCE_BASE_PATH, app, 'distance_harmonic.npy']), distance_matrix_report)

for app in APPS:
	calculate_distance(app) # calculate and save hybrid distance between reports