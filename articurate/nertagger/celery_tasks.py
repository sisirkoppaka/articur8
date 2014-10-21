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
from articurate.metrics import metrics
from celery import current_task
from celery.utils.log import get_task_logger

from articurate.utils.config import *
from articurate.pymotherlode import api

import simplejson as json

logger = get_task_logger(__name__)

@celery.task
def run_nertag():

    # get latest dump of articles
    #articles = article_loader.get_latest_dump()
    articles = article_loader.getAllDumps()

    print "Got so many articles: ", len(articles)

    ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']    

    try:
        print "run_nertag: starting ", ner_types
        
        if config['nertag.content']:
            all_content = [article.content for count, article in enumerate(articles)]
        else:
            all_content = [article.title for count, article in enumerate(articles)]            

        result = chord(parse_NER_celery.s(article, count, ner_types) for count, article in enumerate(all_content))(save_celery.s(kwargs={'ner_types': ner_types}))
        
        print "run_nertag: done! ", ner_types
        return 'True'

    except:
        return 'False'

@celery.task
@metrics.track
def save_celery(results, **kwargs):
    print "save_celery: starting "
        
    ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']
   
    # get what is currently present in redis db
    try:
        final_dict = json.loads(api.getMetric("articurate.nertagger.celery_tasks.save_celery"))
    except:
        final_dict = None
        pass

    if final_dict == None:
        final_dict = {}

    for item in ner_types:
        value = final_dict[item] if item in final_dict else []
        for dictionary in results:
            value.extend(dictionary[item])
        value = list(set(value))
        final_dict[item] = value 

    # # save result to file
    # final_dict = {}
    # for item in ner_types:
    #     value = []
    #     for dictionary in results:
    #         value.extend(dictionary[item])
    #     value = list(set(value))
    #     final_dict[item] = value    
               
    ner_file = open("nertagger.log",'w')
    ner_file.write(json.dumps(final_dict, indent="  "))
    ner_file.close()        

    print "save_celery: done! "
    
    return json.dumps(final_dict, indent="  ")


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

        if len(tags) < 2:
            continue

        previous_tag = tags[0][1]
        string = tags[0][0].lower()
        index = 1
        while index < len(tags):
            current_tag = tags[index][1]

            
            if current_tag == previous_tag:
                string = string + " " + tags[index][0].lower()
            else:
                if previous_tag in ner_types:
                    value = result[previous_tag]                   
                    value.append(string.lower())
                    result[previous_tag] = value            
                string = tags[index][0].lower()

            previous_tag = current_tag
            index = index + 1        

        if previous_tag in ner_types:
            value = result[previous_tag]                   
            value.append(string.lower())
            result[previous_tag] = value

    # convert to set
    for item in ner_types:
        value = result[item]
        value = list(set(value))
        result[item] = value

    print "Article number done:", articleCount, "\n"
    return result
