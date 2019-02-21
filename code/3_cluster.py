#-*- coding:utf-8 -*-
import os, csv
import numpy as np
import scipy.cluster.hierarchy as sch

from variables import APPS
from variables import DISTANCE_BASE_PATH, DUPLICATES_REPORT_PATH
from variables import T_THRESHOLD

from util_corpus import get_all_reports

# ---------------------------------------------------------------------------------------
# Description   : Function to aggregate the reports into groups
# ---------------------------------------------------------------------------------------

def cluster(app):
	all_reports = get_all_reports(app)
	distance_matrix = np.load('/'.join([DISTANCE_BASE_PATH, app, 'distance_harmonic.npy']))
	distArray = distance_matrix[np.triu_indices(len(distance_matrix), 1)]

	Z = sch.linkage(distArray, method = 'single')
	clusters = sch.fcluster(Z, T_THRESHOLD, criterion = 'distance')

	duplicate_set = {}
	for i, cluster_id in enumerate(clusters):
		report = all_reports[i]

		if cluster_id not in duplicate_set.keys():
			duplicate_set[cluster_id] = [report]
		else:
			duplicate_set[cluster_id].append(report)

	if not os.path.exists('/'.join([DUPLICATES_REPORT_PATH, app])):
		os.makedirs('/'.join([DUPLICATES_REPORT_PATH, app]))

	# save duplicate_set
	out = open('/'.join([DUPLICATES_REPORT_PATH, app, 'duplicate_set.csv']), 'wb+')
	writer = csv.writer(out)
	for k in duplicate_set.keys():
		records = duplicate_set[k]
		writer.writerow(records)
	out.close()

for app in APPS:
	cluster(app)
