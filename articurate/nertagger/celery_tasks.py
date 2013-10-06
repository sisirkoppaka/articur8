from __future__ import absolute_import

#Because nertag.py imports below, but isn't available in context of workers
import re
import os
from nltk.tag.stanford import NERTagger
import time
import pickle

from celery import chord
from articurate.celery import celery
from articurate.nertagger import nertag
import articurate.utils.loader as article_loader
import articurate

from celery import current_task


@celery.task
def run_nertag():
	try:
		articles = article_loader.get_latest_dump()
		ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']
		for i, ner_type in enumerate(ner_types):
			print "run_nertag: starting with ", ner_type
			run_nertag_by_type.delay(articles, ner_type)
		print "run_nertag: done!"
		return 'True'
	except:
		return 'False'

@celery.task
def run_nertag_by_type(articles, ner_type):
	try:
		print "run_nertag_by_type: starting ", ner_type
		all_content = [article.content for article in articles[]]
		result = chord((parse_NER_celery.s(article, count, ner_type) for count, article in enumerate(all_content)))(save_celery.s(kwargs={'ner_type': ner_type}))
		result.get()
		print "run_nertag_by_type: done! ", ner_type
		return 'True'
	except:
		return 'False'

@celery.task
def save_celery(ner_list, **kwargs):
	try:
		print "save_celery: starting "
		request = current_task.request
		ner_list_actual = []
		for i, nestedItem in enumerate(ner_list):
			for j, actualItem in enumerate(nestedItem):
				ner_list_actual.append(actualItem)
		ner_list_actual = set(ner_list_actual)
		ner_types = {'ORGANIZATION':'org_list.log', 'LOCATION':'loc_list.log', 'PERSON':'per_list.log'}
		ner_file = open(ner_types[request.kwargs['kwargs']['ner_type']],'w')
		pickle.dump(ner_list_actual,ner_file)
		ner_file.close()
		return 'True'
	except:
		return 'False'



@celery.task
def parse_NER_celery(document, articleCount, ner_type):
    
    ner_list = []

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
        tags = st.tag(sentence.encode('utf-8').split())
        ner_list.extend([item[0] for item in tags if item[1] == ner_type])

    print "Article number done:", articleCount, "\n"
    return ner_list