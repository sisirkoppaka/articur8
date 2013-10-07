from __future__ import absolute_import

#Because nertag.py imports below, but isn't available in context of workers
import re
import os
from nltk.tag.stanford import NERTagger
import time
import pickle

from itertools import izip
from collections import defaultdict

from celery import chord, group
from articurate.celery import celery
from articurate.nertagger import nertag
import articurate.utils.loader as article_loader
import articurate

from celery import current_task
from celery.utils.log import get_task_logger

import simplejson as json

logger = get_task_logger(__name__)

@celery.task
def run_nertag():

    articles = article_loader.get_latest_dump()
    ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']    

    try:
        print "run_nertag_by_type: starting ", ner_types

        #all_content = [article.content for count, article in enumerate(articles) if count < 5 ]
        all_content = [article.content for count, article in enumerate(articles)]

        #result = chord(parse_NER_celery.s(article, count, ner_types) for count, article in enumerate(all_content))(save_celery.s(kwargs={'ner_types': ner_types}))		
        #result = group(parse_NER_celery.s(article, count, ner_types) for count, article in enumerate(all_content))()
        
        g = group(parse_NER_celery.s(article, count, ner_types) for count, article in enumerate(all_content))
        result = g.apply_async()
        result.get(interval=10000)
        print result

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

    print "Starting document no. %d"%articleCount
	
    result = {} # stores list of tokens associated with each ner_type
    for item in ner_types:
        result[item] = []


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
        print "%d:%d/%d"%(articleCount, count, len(sentences))
        tags = st.tag(sentence.encode('utf-8').split())

        for item in tags:
            if item[1] in ner_types: # is one of the tags we are interested in
                values = result[item[1]] 
                values.append(item[0])
                result[item[1]] = values

    print "Article number done:", articleCount, "\n"
    print result
    return result
