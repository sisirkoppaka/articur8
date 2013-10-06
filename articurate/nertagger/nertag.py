# coding: utf-8
import re
import os
from nltk.tag.stanford import NERTagger
import time
import pickle

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
        
    for count, article in enumerate(articles):
        print "Article number:", count, "\n"
        parse_NER(article.content)
    
    org_list = set(org_list)
    loc_list = set(loc_list)
    per_list = set(per_list)

    loc_file = open('loc_list.txt', 'w')
    pickle.dump(loc_list, loc_file)
    loc_file.close()

    org_file = open('org_list.txt', 'w')
    pickle.dump(org_list, org_file)
    org_file.close()

    per_file = open('per_list.txt', 'w')
    pickle.dump(per_list, per_file)
    per_file.close()

   
