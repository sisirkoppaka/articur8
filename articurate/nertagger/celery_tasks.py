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
        print "run_nertag: starting ", ner_types

        all_content = [article.content for count, article in enumerate(articles)]

        result = chord(parse_NER_celery.s(article, count, ner_types) for count, article in enumerate(all_content))(save_celery.s(kwargs={'ner_types': ner_types}))

        #print "Done ::", len(result)
        
        print "run_nertag_by_type: done! ", ner_types
        return 'True'
    except:
        return 'False'

@celery.task
def save_celery(results, **kwargs):
    print "save_celery: starting "
        
    ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']
   
    # save result to file
    final_dict = {}
    for item in ner_types:
        value = []
        for dictionary in results:
            value.extend(dictionary[item])
        value = list(set(value))
        final_dict[item] = value    
               
    ner_file = open("nertagger.log",'w')
    ner_file.write(json.dumps(final_dict, indent="  "))
    ner_file.close()        

    print "save_celery: done! "
    


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
        string = tags[0][0]
        index = 1
        while index < len(tags):
            current_tag = tags[index][1]

            
            if current_tag == previous_tag:
                string = string + " " + tags[index][0]
            else:
                if previous_tag in ner_types:
                    value = result[previous_tag]                   
                    value.append(string)
                    result[previous_tag] = value            
                string = tags[index][0]

            previous_tag = current_tag
            index = index + 1        

        if previous_tag in ner_types:
            value = result[previous_tag]                   
            value.append(string)
            result[previous_tag] = value

    # convert to set
    for item in ner_types:
        value = result[item]
        value = list(set(value))
        result[item] = value

    print "Article number done:", articleCount, "\n"
    return result
