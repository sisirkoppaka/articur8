"""Connect to the Motherlode"""

import requests
import jsonpickle

SERVER_URL = "http://localhost:9999/"

def storeDeltaDump(timestamp,deltadump):
    payload = {'timestamp':timestamp,'deltadump':deltadump}
    r = requests.post(SERVER_URL+"dumps/delta/",data=payload)

def storeCluster(clusterInJSON, tag):
    payload = {'clusterInJSON':clusterInJSON,'tag':tag}
    r = requests.post(SERVER_URL+"clusters/latest/",data=payload)    

def getLatestCluster():
 	r = requests.get(SERVER_URL+"clusters/latest/")
 	return r.content

def getLatestDeltaDump():
 	r = requests.get(SERVER_URL+"dumps/delta/latest")
 	return r.content

def getDeltaDump(timestamp):
	r = requests.get(SERVER_URL+"dumps/delta"+timestamp)
	return r.content

def storeMetric(method, obj):
	methodPayload = jsonpickle.encode(obj)
	payload = {'method':method, 'methodPayload':methodPayload}
	r = requests.post(SERVER_URL+"metrics/track/",data=payload)    

def getMetric(method):
	 r = requests.get(SERVER_URL+"metrics/track/"+method)
	 return jsonpickle.decode(r.content)


