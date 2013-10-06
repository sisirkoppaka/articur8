from __future__ import absolute_import

from articurate.celery import celery
from articurate.fd.celery_tasks import *
from articurate.nertagger.celery_tasks import *

@celery.task
def add(x, y):
    return x + y

@celery.task
def xsum(numbers):
    return sum(numbers)