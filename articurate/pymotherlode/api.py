"""Connect to the Motherlode"""

import requests
import jsonpickle
import redis
from articurate.utils.config import *

SERVER_URL = "http://localhost:9999/"

def storeDeltaDump(timestamp,deltadump):
    payload = {'timestamp':timestamp,'deltadump':deltadump}
    r = requests.post(SERVER_URL+"dumps/delta/",data=payload)

def storeCluster(clusterInJSON, tag):
    payload = {'clusterInJSON':clusterInJSON,'tag':tag}
    r = requests.post(SERVER_URL+"clusters/latest/",data=payload)  
    print r, r.content  

def getLatestCluster():
 	r = requests.get(SERVER_URL+"clusters/latest/")
 	return r.content

def getLatestDeltaDump():
 	r = requests.get(SERVER_URL+"dumps/delta/latest")
 	return r.content

def getDeltaDump(timestamp):
	r = requests.get(SERVER_URL+"dumps/delta/"+timestamp)
	return r.content

def storeMetric(method, obj):
	methodPayload = jsonpickle.encode(obj)
	payload = {'method':method, 'methodPayload':methodPayload}
	r = requests.post(SERVER_URL+"metrics/track/",data=payload)    

def getMetric(method):
	r = requests.get(SERVER_URL+"metrics/track/"+method)
	return jsonpickle.decode(r.content)

def getMetricByKey(method, key):
	r = requests.get(SERVER_URL+"metrics/track/"+method+"_"+key)
	return jsonpickle.decode(r.content)	

def updateDumpKeyCache(timestamp):
	# try to get the key cache
	r_server = redis.StrictRedis(host='localhost',port=6379, db=0)
	cacheLen = r_server.llen("dumpKeyCache")

	if cacheLen == config['dump.keyCacheSize']: # cache is full, pop oldest element
		r_server.lpop("dumpKeyCache")

	r_server.rpush("dumpKeyCache", timestamp)

def getAllCacheDumps():

	# try to get the key cache
	r_server = redis.StrictRedis(host='localhost',port=6379, db=0)
	cacheLen = r_server.llen("dumpKeyCache")

	if cacheLen == 0: # no dumps found
		return []

	# collect all dumps in cache
	values = []
	keys = r_server.lrange("dumpKeyCache", 0, -1)
	for key in keys:
		values.append(getDeltaDump(key))

	print "Got so many keys ", len(values)

	return values



