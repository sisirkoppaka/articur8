# coding: utf-8
import re
import os
from nltk.tag.stanford import NERTagger
import time

from articulate.pymotherlode.api import *
import articulate.utils.loader as loader

import articulate

# global variables
org_list = []
loc_list = []
per_list = []

def parse_NER(document):
    
    # split text into sentences
    sentenceEnders = re.compile('[.!?]')
    sentences = sentenceEnders.split(document)
    total = len(sentences)
    
    #initialize paths
    englishPath = os.path.join(os.path.join(os.path.dirname(articulate.__file__),'nertagger'),'english.all.3class.distsim.crf.ser.gz')
    stanfordNERPath = os.path.join(os.path.join(os.path.dirname(articulate.__file__),'nertagger'),'stanford-ner.jar')
    
    # initialize tagger
    st = NERTagger(englishPath, stanfordNERPath)
   
    # tag each sentence
    for count, sentence in enumerate(sentences):

        print count, "/", total

        tags = st.tag(sentence.encode('utf-8').split())

        # add to list of tagged items
        org_list.extend([item[0] for item in tags if item[1] == 'ORGANIZATION'])
        loc_list.extend([item[0] for item in tags if item[1] == 'LOCATION'])
        per_list.extend([item[0] for item in tags if item[1] == 'PERSON'])


if __name__ == '__main__':

    # get articles from wherever
    articles = loader.get_latest_dump()
        
    parse_NER(articles[0].content)
    
    org_list = set(org_list)
    loc_list = set(loc_list)
    per_list = set(per_list)

    print "Org :", org_list
    print "Loc :", loc_list
    print "Per :", per_list
 

  
