from __future__ import absolute_import

#Because nertag.py imports below, but isn't available in context of workers
import re
import os
from nltk.tag.stanford import NERTagger
import time
import pickle

from itertools import izip
from collections import defaultdict

from celery import chord
from articurate.celery import celery
from articurate.nertagger import nertag
import articurate.utils.loader as article_loader
import articurate

from celery import current_task

import simplejson as json


@celery.task
def run_nertag():
	try:
		articles = article_loader.get_latest_dump()
		ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']
		#for i, ner_type in enumerate(ner_types):
		print "run_nertag: starting with "
		run_nertag_by_type.delay(articles, ner_types)
		print "run_nertag: done!"
		return 'True'
	except:
		return 'False'

@celery.task
def run_nertag_by_type(articles, ner_types):
	try:
		print "run_nertag_by_type: starting ", ner_types
		all_content = [article.content for article in articles ]
		result = chord((parse_NER_celery.s(article, count, ner_types) for count, article in enumerate(all_content)))(save_celery.s(kwargs={'ner_types': ner_types}))
		result.get()
		print "run_nertag_by_type: done! ", ner_types
		return 'True'
	except:
		return 'False'

@celery.task
def save_celery(ner_list, **kwargs):
	print "save_celery: starting "
	print ner_list
	request = current_task.request
	ner_list_actual = ner_list #[]
	#for i, nestedItem in enumerate(ner_list):
	#	for j, actualItem in enumerate(nestedItem):
	#		ner_list_actual.append(actualItem)
	#ner_list_actual = set(ner_list_actual)
	#ner_types = {'ORGANIZATION':'org_list.log', 'LOCATION':'loc_list.log', 'PERSON':'per_list.log'}
	#ner_file = open(ner_types[request.kwargs['kwargs']['ner_type']],'w')
	ner_file = open("nertagger.log",'w')
	ner_file.write(json.dumps(ner_list_actual, indent="  "))
	#pickle.dump(ner_list_actual,ner_file)
	ner_file.close()



@celery.task
def parse_NER_celery(document, articleCount, ner_types):
	
	ner_list = []
	ner_type_list = []
	# split text into sentences
	sentenceEnders = re.compile('[.!?]')
	sentences = sentenceEnders.split(document)
	total = len(sentences)
	
	#initialize paths
	englishPath = os.path.join(os.path.join(os.path.dirname(articurate.__file__),'nertagger'),'english.all.3class.distsim.crf.ser.gz')
	stanfordNERPath = os.path.join(os.path.join(os.path.dirname(articurate.__file__),'nertagger'),'stanford-ner.jar')
	
	# initialize tagger
	st = NERTagger(englishPath, stanfordNERPath)
   
	# tag each sentence
	for count, sentence in enumerate(sentences):
		ner_entry = []
		ner_type_entry=[]
		tags = st.tag(sentence.encode('utf-8').split())
		for index, ner_type in enumerate(ner_types):
			ner_entry.extend([item[0] for item in tags if item[1] == ner_type])
			ner_entry.extend([None for item in tags if item[1] != ner_type])
			ner_type_entry.extend([item[1] for item in tags if item[1] == ner_type])
			ner_type_entry.extend([None for item in tags if item[1] != ner_type])        	

		ner_list.extend(ner_entry)
		ner_type_list.extend(ner_type_entry)
	#response = defaultdict(['ORGANIZATION', 'LOCATION', 'PERSON'])
	#collect = defaultdict(['ORGANIZATION', 'LOCATION', 'PERSON'])
	# print ner_type_list
	# response = defaultdict(list)
	# collect = defaultdict(list)
	# wasPrevNone = 0
	# prevTagType = ""
	# sendPrevWord = 0
	# i = 0
	# i_old = -1
	# for tagWord, tagType in izip(ner_list, ner_type_list):
	# 	i = i+1
	# 	if tagType is None:
	# 		if wasPrevNone == 0:
	# 			if (i-i_old) == 1:
	# 				toAdd = (" "+(collect[prevTagType]))
	# 				response[prevTagType][-1] += toAdd
	# 				collect = defaultdict(list)#ner_types)
	# 				i_old = i
	# 			else:    
	# 				response[prevTagType].extend((collect[prevTagType]))
	# 				collect = defaultdict(list)#ner_types)
	# 				i_old = i
	# 		wasPrevNone = 1
	# 		prevTagType = None    		
	# 		continue
	# 	else:
	# 		if not wasPrevNone:
	# 			collect[tagType].append(tagWord)
	# 		else:
	# 			collect[tagType] += tagWord
	# 		prevTagType = tagType
	# 		wasPrevNone = 0


	print "Article number done:", articleCount, "\n"
	return {'tags': ner_list, 'tagTypes': ner_type_list}