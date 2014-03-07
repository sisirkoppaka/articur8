from articurate.pymotherlode.api import *
import articurate.utils.loader as loader

import clusterer, clusterformats

from articurate.pymotherlode import api
import jsonpickle
from articurate.utils.class_definitions import ParamObj     

import math

# get articles from wherever
#articles = loader.get_latest_dump()
articles = loader.collect_last_dumps()

# define parameters
params = ParamObj(100, 'nmf', True) # (num_clusters, clustering_method, only_titles)

# get clusters, result has assignment list and cluster objects
result = clusterer.cluster(articles, params)

# print output
for cluster in result['clusters']:
	value1 = math.log(1.1 + cluster.metrics['avg_named_entities'])
	value2 = math.log(cluster.metrics['num_articles'])
	value3 = cluster.metrics['avg_distance_from_center']+10+0.1
	score = value1 * value2 / (value3*value3)
	print cluster.identifier, ":", len(cluster.article_list), ":", cluster.closest_article.title, "\n", value1, value2, value3, score, "\n", cluster.metrics

# stores a copy of the cluster in JSON in the motherlode, with or without content
#clusterformats.clustersToJSON(articles, result['assignment']) #Deprecated
clusterformats.clustersToJSONNew(result['clusters']) #Deprecated

#cluster = api.getMetric("articurate.clustering.clusterer.cluster")
#print "from metrics", cluster['assignment']
