#-*- coding:utf-8 -*-
import os, csv, json
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer
from variables import POS_TAGS, APPS
from variables import CORPUS_PATH, HIST_TXT_PATH

# ---------------------------------------------------------------------------------------
# Description   : Function to calculate textual features of reports
# ---------------------------------------------------------------------------------------

def parse_corpus(_corpus):
	for tag in POS_TAGS:
		_corpus = _corpus.replace(tag, '')
	_corpus = _corpus.replace('_n', '')
	return _corpus

def load_corpus(app):
	corpus = []
	for name in sorted(os.listdir('/'.join([CORPUS_PATH, app]))):
		_corpus_file = open('/'.join([CORPUS_PATH, app, name]), 'rb')
		_corpus = _corpus_file.read().replace('\n','')
		corpus.append(parse_corpus(_corpus))
	return corpus

def generate_hist(app):
	corpus = load_corpus(app)
	vectorizer = TfidfVectorizer(norm=u'l1', max_features=100)
	X = vectorizer.fit_transform(corpus)
	save_npz('/'.join([HIST_TXT_PATH, app+'.npz']), X) # save text hist


for app in APPS:
	generate_hist(app) # for each group, generate its text hist