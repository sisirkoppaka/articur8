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
				#try:
				#	lede = getLede(articles[j].content)
				#except:
				#	lede = ''

				lede = getLede(articles[j].content)

				if insertContent:
					#With Content
					articlesInCluster.append({'title':articles[j].title, 'feed_title':articles[j].feed_title, 'link':articles[j].link, 'author':articles[j].author, 'lede':lede, 'content':articles[j].content, 'updated_at':articles[j].updated_at})
				else:
					#And Without
					articlesInCluster.append({'title':articles[j].title, 'feed_title':articles[j].feed_title, 'link':articles[j].link, 'author':articles[j].author, 'lede':lede, 'updated_at':articles[j].updated_at})

		clustersForHumans.append({'cluster': i,'articles':articlesInCluster})

	storeCluster(json.dumps(clustersForHumans),tag)


def clustersToJSONNew(clusters):
	tag = "kmeans"
	#clusters = list(set(assignments))

	clustersForHumans = []

	insertContent = config['clusterFormats.insertContent']

	if insertContent:
		print "Inserting content into ClusterInJSON"
	else:
		print "Not inserting content into ClusterInJSON"

	for i, cluster in enumerate(clusters):
		articlesInCluster = []
		for j, article in enumerate(cluster.article_list):
			lede = getLede(article.content)
			if insertContent:
				#With Content
				articlesInCluster.append({'title':article.title, 'feed_title':article.feed_title, 'link':article.link, 'author':article.author, 'lede':lede, 'content':article.content, 'updated_at':article.updated_at})
			else:
				#And Without
				articlesInCluster.append({'title':article.title, 'feed_title':article.feed_title, 'link':article.link, 'author':article.author, 'lede':lede, 'updated_at':article.updated_at})

		article = cluster.closest_article;

		hash_string = article.title + " " + article.feed_title + " " + article.author
		hash_value = hashlib.md5(hash_string.encode('utf-8')).hexdigest()

		closest_article = {'title':article.title, 'feed_title':article.feed_title, 'link':article.link, 'author':article.author, 'lede':lede, 'content':article.content, 'updated_at':article.updated_at}

		clustersForHumans.append({'cluster': i, 'hash': hash_value,'closest_article': closest_article, 'articles':articlesInCluster})

	storeCluster(json.dumps(clustersForHumans),tag)

#if __name__ == "__main__":
#	hello()
#	articles = []
#	assignments = []
#	clustersToJSON(articles,assignments)
