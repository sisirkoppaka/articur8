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
params = {}
params['nmf'] = ParamObj(100, 'nmf', True) # (num_clusters, clustering_method, only_titles)
params['gaac'] = ParamObj(100, 'gaac', True)

# get clusters, result has assignment list and cluster objects
result = {}
result['nmf'] = clusterer.cluster(articles, params['nmf'])
#result['gaac'] = clusterer.cluster(articles, params['gaac'])

# find robust clusters, supported by both clustering methods
#result['combined'] = clusterer.find_robust_clusters(result)

# print output
#for cluster in result['nmf']['clusters']:
#	print cluster.identifier, ":", len(cluster.article_list), ":", cluster.closest_article.title, "\n"

# stores a copy of the cluster in JSON in the motherlode, with or without content
clusterformats.clustersToJSONNew(result['nmf']['clusters']) #Deprecated