from articurate.pymotherlode.api import *
import articurate.utils.loader as loader

import clusterer, clusterformats

from articurate.pymotherlode import api
import jsonpickle


class ParamObj:
	
	""" Define parameters to use for clustering articles

	"""

    def __init__(self, num_clusters, clustering_method, only_titles):
        self.num_clusters = num_clusters
        self.clustering_method = clustering_method
        self.only_titles = only_titles



# get articles from wherever
articles = loader.get_latest_dump()

# params
params = ParamObj(20, 'nmf', True)

# get clusters, result has assignment list and cluster objects
result = clusterer.cluster(articles, params)

# print output
for item in result['clusters']:
    print item.identifier, ":", len(item.article_list), ":", item.closest_article.title 

# stores a copy of the cluster in JSON in the motherlode, with or without content
clusterformats.clustersToJSON(articles, result['assignment'])
cluster = api.getMetric("articurate.clustering.clusterer.cluster")
print "from metrics", cluster['assignment']
