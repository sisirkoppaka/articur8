# coding: utf-8

from nltk.tag.stanford import NERTagger
import time
from articulate.pymotherlode.api import *

def parse_NER(string):
 
    st = NERTagger('english.all.3class.distsim.crf.ser.gz', 'stanford-ner.jar')
   
    return st.tag(string.split())


if __name__ == '__main__':
    
  
## get data here from motherlode    
#Motherlode should be accessible now
  
