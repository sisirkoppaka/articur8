from __future__ import absolute_import

from articurate.celery import celery

from articurate.fd import fd

@celery.task
def runFD():
	try:
		fd.startFD()
		return 'True'
	except:
		return 'False'