#-*- coding:utf-8 -*-
import os, csv, sys, re
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import SentenceSplitter
from variables import APPS, HEADER
from variables import RAW_PATH, CORPUS_PATH, STOP_WORDS_PATH, SYNONYM_WORDS_PATH
from variables import cws_model_path, pos_model_path

# ---------------------------------------------------------------------------------------
# Description   : Function to preprocess the raw reports
# ---------------------------------------------------------------------------------------

def read_stop_words():
	stop_words = []
	f = open(STOP_WORDS_PATH, 'rb')
	for line in f.readlines():
		stop_words.append(line.replace('\n','').replace('\r',''))
	f.close()
	return stop_words

def read_synonym_words():
	synonym_words = {}
	f = open(SYNONYM_WORDS_PATH, 'rb')
	for line in f.readlines():
		_from, _to = line.replace('\n','').replace('\r','').split('\t')
		synonym_words[_from] = _to
	f.close()
	return synonym_words

def preprocess(app):
	segmentor = Segmentor()
	segmentor.load(cws_model_path)
	postagger = Postagger()
	postagger.load(pos_model_path)

	stop_words = read_stop_words()
	synonym_words = read_synonym_words()

	with open('/'.join([RAW_PATH, 'report_'+app+'.csv'])) as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		head_row = reader.next()
		for row in reader:
			_id = row[HEADER['id']]
			_description = row[HEADER['description']]
			_description = _description.replace('\n','').replace('\r','').strip()
			if not os.path.isfile('/'.join([CORPUS_PATH, app, _id+'.txt'])):
				sents = SentenceSplitter.split(_description)
				content = []
				for sent in sents:
					words = [w for w in segmentor.segment(sent) if w not in stop_words]
					words = [synonym_words[w] if w in synonym_words.keys() else w for w in words]
					postags = postagger.postag(words)

					items = ['_'.join(x) for x in zip(words, postags)]
					content.append(' '.join(items))
				content = '\n'.join(content)

				f_out = open('/'.join([CORPUS_PATH, app, _id+'.txt']), 'wb+')
				f_out.write(content)
				f_out.close()
	segmentor.release()
	postagger.release()

for app in APPS:
	preprocess(app)