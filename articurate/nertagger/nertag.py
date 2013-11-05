# coding: utf-8

import re
import os
from nltk.tag.stanford import NERTagger
import time
import pickle

from articurate.pymotherlode.api import *
import articurate.utils.loader as loader
from celery_tasks import *

import articurate

def run_with_celery():
    #This version of celery_tasks for nertag are optimal if you have more than 3 cores/hyperthreads.
    print "run_with_celery: starting "
    run_nertag.delay()    

if __name__ == '__main__':
    ner_types = ['ORGANIZATION', 'LOCATION', 'PERSON']

    #run_single_threaded()

    #Do 0,1,2 in different runs for now, until some alternate solution is found
    run_with_celery()



   
