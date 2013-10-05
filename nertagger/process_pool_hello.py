# coding: utf-8

from nltk.tag.stanford import NERTagger
import time

def parse_NER(string):
 
    st = NERTagger('english.all.3class.distsim.crf.ser.gz', 'stanford-ner.jar')
   
    return st.tag(string.split())


if __name__ == '__main__':
    
  
## get data here from motherlode    
  
