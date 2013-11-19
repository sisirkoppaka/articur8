from fabric.api import *
from fabric.colors import green, red

import psutil
import re
import redis

from articurate.fd.fd import startFD

#Start Motherlode
def start_motherlode(debug='False'):
	if debug=='False':
		local("cd ./articurate/motherlode && node app.js > /dev/null 2>&1 &")
		print green("start_motherlode: Started Motherlode with Debug mode set to "+debug, bold=True)
	else:
		local("cd ./articurate/motherlode && node app.js > ../../motherlode.log 2>&1 &")
		print green("start_motherlode: Started Motherlode with Debug mode set to "+debug, bold=True)


#Stop Motherlode
def stop_motherlode():
	found = 'False';
	for proc in psutil.process_iter():
		try:
			match = re.match(r'.*node.*',proc.name)
			if match:
				print green("stop_motherlode: Found process, stopping "+match.group()+".", bold=True)
				proc.kill()
				found = 'True'
		except:
			continue

	#The below seems to not work, fix me.
	if not found:
		print green("stop_motherlode: Could not find process for Motherlode", bold=True)

#Restart Motherlode
def restart_motherlode(debug='False'):
	stop_motherlode()
	start_motherlode(debug)
	print green("restart_motherlode: Finished restarting Motherlode ", bold=True)	

#Setup Motherlode
def setup_motherlode():
	local("cd ./articurate/motherlode && npm install")
	print green("setup_motherlode: Finished satisfying prerequisites for Motherlode ", bold=True)

#Start Celery Worker
def start_celery_worker(debug='False'):
	if debug=='False':
		local('celery worker --app=articurate.celery -l info > /dev/null 2>&1 &')
		print green("start_celery_worker: Started Celery Worker with Debug mode set to "+debug, bold=True)
	else:
		local("celery worker --app=articurate.celery -l info > ./celery.log 2>&1 &")
		print green("start_motherlode: Started Motherlode with Debug mode set to "+debug, bold=True)

#Stop Celery Worker - REVISE later, works now
def stop_celery_worker():
	found = 'False';
	#for proc in psutil.process_iter():
		#try:
			#match = re.match(r'.*celery.*',proc.name)
	#	match = re.search(r'.*celery.*',proc.name)
	#	if match:
	#		print green("stop_celery_worker: Found process, stopping "+match.groups()+".", bold=True)
	#		proc.kill()
	#		found = 'True'
		#except:
		#	pass

	#The below seems to not work, fix me.
	#if not found:
	#	print green("stop_celery_worker: Could not find process for Celery Worker", bold=True)
	try:
		local("ps auxww | grep celery | awk '{print $2}' | xargs kill -9")
		print green("stop_celery_worker: Killed", bold=True)
	except:
		pass
	#print green("stop_celery_worker: Killed", bold=True)

def flush_celery_redis():
	try:
		r = redis.StrictRedis(host='localhost',port=6379, db=1)
		r.flushdb()
	except:
		pass

#Restart Motherlode
def restart_celery_worker(debug='False'):
	stop_celery_worker()
	flush_celery_redis()
	start_celery_worker(debug)
	print green("restart_celery_worker: Finished restarting Celery Worker ", bold=True)

#Kickstart everything
def kickstart(debug='False'):
	setup_motherlode()
	start_motherlode(debug)
	start_celery_worker(debug)
	print green("kickstart: Done!", bold=True)

#Kickstop everything
def kickstop():
	stop_motherlode()
	stop_celery_worker()
	flush_celery_redis()
	print green("kickstop: Done!", bold=True)

#Kickrestart everything
def kickrestart(debug='False'):
	kickstop()
	kickstart(debug)
	print green("kickrestart: Done!", bold=True)

def runFD():
	startFD()

