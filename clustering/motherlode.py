"""Connect to the Motherlode"""

import requests

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

 
