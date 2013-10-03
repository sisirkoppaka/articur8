"""Clusters for Humans"""

import itertools
import simplejson as json

def clustersToJSON(articles, assignments):
	clusters = list(set(assignments))

	clustersForHumans = []

	for i in clusters:
		articlesInCluster = []
		for j, cluster in enumerate(assignments):
			if cluster == i:
				articlesInCluster.append({'title':articles[j].title, 'feed_title':articles[j].feed_title, 'link':articles[j].link, 'author':articles[j].author, 'content':articles[j].content, 'updated_at':articles[j].updated_at})

		clustersForHumans.append({'cluster': i,'articles':articlesInCluster[0]})

	return json.dumps(clustersForHumans)

def hello():
	print "hello"

#if __name__ == "__main__":
#	hello()
#	articles = []
#	assignments = []
#	clustersToJSON(articles,assignments)