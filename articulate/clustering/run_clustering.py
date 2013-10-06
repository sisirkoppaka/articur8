from articulate.pymotherlode.api import *
import articulate.utils.loader as loader

import clusterer


class ParamObj:

    def __init__(self, num_clusters, clustering_method):
        self.num_clusters = num_clusters
        self.clustering_method = clustering_method


# get articles from wherever
articles = loader.get_latest_dump()

# params
params = ParamObj(10, 'nmf')

# modify article obj as needed and get clusters
clusters = clusterer.cluster(articles, params)

# print output
for item in clusters:
    print item.identifier, ":", item.closest_article.title

#Stores a copy of the cluster in JSON in the motherlode, with or without content
clusterformats.clustersToJSON(articles, assignment)


