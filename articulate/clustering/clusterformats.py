"""Clusters for Humans"""

import itertools
import simplejson as json
from articulate.pymotherlode.api import *

def clustersToJSON(articles, assignments, insertContent):
	tag = "kmeans"
	clusters = list(set(assignments))

	clustersForHumans = []

	if insertContent:
		print "Inserting content into ClusterInJSON"
	else:
		print "Not inserting content into ClusterInJSON"

	for i in clusters:
		articlesInCluster = []
		for j, cluster in enumerate(assignments):
			if cluster == i:
				if insertContent:
					#With Content
					articlesInCluster.append({'title':articles[j].title, 'feed_title':articles[j].feed_title, 'link':articles[j].link, 'author':articles[j].author, 'content':articles[j].content, 'updated_at':articles[j].updated_at})
				else:
					#And Without
					articlesInCluster.append({'title':articles[j].title, 'feed_title':articles[j].feed_title, 'link':articles[j].link, 'author':articles[j].author, 'updated_at':articles[j].updated_at})

		clustersForHumans.append({'cluster': i,'articles':articlesInCluster})

	storeCluster(json.dumps(clustersForHumans),tag)

#if __name__ == "__main__":
#	hello()
#	articles = []
#	assignments = []
#	clustersToJSON(articles,assignments)