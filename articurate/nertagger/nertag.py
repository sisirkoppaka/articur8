# coding: utf-8

# import re
# import os
# from nltk.tag.stanford import NERTagger
# import time
# import pickle

# from articurate.pymotherlode.api import *
# import articurate.utils.loader as loader

# from celery_tasks import *
 
import celery_tasks


if __name__ == '__main__':

    celery_tasks.run_nertag.delay()   



   
