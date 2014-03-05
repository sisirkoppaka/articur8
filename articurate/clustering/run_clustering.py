from articurate.pymotherlode.api import *
import articurate.utils.loader as loader

import clusterer, clusterformats

from articurate.pymotherlode import api
import jsonpickle
from articurate.utils.class_definitions import ParamObj     

# get articles from wherever
#articles = loader.get_latest_dump()
articles = loader.collect_last_dumps()

# define parameters
params = ParamObj(50, 'gaac', True) # (num_clusters, clustering_method, only_titles)

# get clusters, result has assignment list and cluster objects
result = clusterer.cluster(articles, params)

# print output
for item in result['clusters']:
    print item.identifier, ":", len(item.article_list), ":", item.closest_article.title, "\n", item.metrics 

# stores a copy of the cluster in JSON in the motherlode, with or without content
#clusterformats.clustersToJSON(articles, result['assignment']) #Deprecated
clusterformats.clustersToJSONNew(result['clusters']) #Deprecated

#cluster = api.getMetric("articurate.clustering.clusterer.cluster")
#print "from metrics", cluster['assignment']
