import requests

#Testing with text
payload = {'timestamp': '201309282105','deltadump':'wassup'}
r = requests.post("http://localhost:9999/dumps/delta/",data=payload)

print r.text

#Testing with a real dump file
f = open('201309282106.opml','r')
payloadOPML = {'timestamp':'201309282106','deltadump':f.read()}
rOPML = requests.post("http://localhost:9999/dumps/delta/",data=payloadOPML)

print rOPML.text

#Testing if the latest file GET works
rLATEST = requests.get("http://localhost:9999/dumps/delta/latest")

print rLATEST.content #Should return the OPML file

#Testing if the GET-by-timestamp works
rTIMESTAMP = requests.get("http://localhost:9999/dumps/delta/201309282105")

print rTIMESTAMP.content
