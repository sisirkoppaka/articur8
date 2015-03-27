"""Clusters for Humans"""

import itertools
import hashlib
import simplejson as json
from articurate.pymotherlode.api import *
from articurate.utils.config import *

def getLede(content):
	
	#ledeRE = re.compile('^(.*?(?<!\b\w)[.?!])\s+[A-Z0-9]')
	#ledes = ledeRE.match(content)
	#return ledes.group(0)
	lede = content[:65]
	lede += "..."

	return lede
	
# getLede() ends

def clustersToJSON(articles, assignments):
	
	tag = "kmeans"

	clusters = list(set(assignments))
	clustersForHumans = []

	insertContent = config['clusterFormats.insertContent']
	if insertContent:
		print "Inserting content into ClusterInJSON"
	else:
		print "Not inserting content into ClusterInJSON"

	for i in clusters:
		
		articlesInCluster = []
		
		for j, cluster in enumerate(assignments):
			if cluster == i:
				lede = getLede(articles[j].content)
				if insertContent: # with Content
					articlesInCluster.append({'title': articles[j].title, 'feed_title': articles[j].feed_title, 'link': articles[j].link, 'author': articles[j].author, 'lede': lede, 'updated_at': articles[j].updated_at, 'content': articles[j].content})
				else: # and Without
					articlesInCluster.append({'title': articles[j].title, 'feed_title': articles[j].feed_title, 'link': articles[j].link, 'author': articles[j].author, 'lede': lede, 'updated_at': articles[j].updated_at})

		clustersForHumans.append({'cluster': i,'articles':articlesInCluster})

	storeCluster(json.dumps(clustersForHumans),tag)

# clustersToJSON() ends

def clustersToJSONNew(clusters):

	tag = "kmeans"

	clustersForHumans = []

	insertContent = config['clusterFormats.insertContent']
	if insertContent:
		print "Inserting content into ClusterInJSON"
	else:
		print "Not inserting content into ClusterInJSON"

	for i, cluster in enumerate(clusters):
		
		# list of articles in cluster
		articlesInCluster = []
		for j, article in enumerate(cluster.article_list):		
			lede = getLede(article.content)
			if insertContent: # with Content
				articlesInCluster.append({'title': article.title, 'feed_title': article.feed_title, 'link': article.link, 'author': article.author, 'lede':lede, 'updated_at': article.updated_at, 'content': article.content})
			else: # and Without
				articlesInCluster.append({'title': article.title, 'feed_title': article.feed_title, 'link': article.link, 'author': article.author, 'lede':lede, 'updated_at': article.updated_at})

		# the closest article to center
		article = cluster.closest_article;
		closest_article = {'title': article.title, 'feed_title': article.feed_title, 'link': article.link, 'author': article.author, 'lede': lede, 'content': article.content, 'updated_at': article.updated_at}
		
		# generate the hash
		hash_string = article.title + " " + article.feed_title + " " + article.author
		hash_value  = hashlib.md5(hash_string.encode('utf-8')).hexdigest()

		clustersForHumans.append({'cluster': i, 'hash': hash_value, 'closest_article': closest_article, 'articles': articlesInCluster})

	storeCluster(json.dumps(clustersForHumans), tag)

# clustersToJSONNew() ends

#if __name__ == "__main__":
#	hello()
#	articles = []
#	assignments = []
#	clustersToJSON(articles,assignments)
