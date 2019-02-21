#-*- coding:utf-8 -*-
import os
from variables import CORPUS_PATH, DUPLICATES_CLUSTER_PATH

# ---------------------------------------------------------------------------------------
# Description   : Report Corpus Data Processor
# ---------------------------------------------------------------------------------------

def get_all_reports(app):
	all_reports = []
	for report in sorted(os.listdir('/'.join([CORPUS_PATH, app]))):
		report_id = report.split('.')[0]
		all_reports.append(report_id)
	return all_reports

def get_dup_groups(app):
	dup_groups = []
	for report in sorted(os.listdir('/'.join([DUPLICATES_CLUSTER_PATH, app]))):
		dup_groups.append(report)
	return dup_groups

def get_dup_reports_of_one_group(group_id):
	dup_reports = []
	for report in sorted(os.listdir('/'.join([DUPLICATES_CLUSTER_PATH, app, group_id]))):
		report_id = report.split('.')[0]
		if report_id !='':
			dup_reports.append(report_id)
	return dup_reports