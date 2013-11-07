from __future__ import division

import vectorer
import clusterformats
from clustering_algos import *

from articurate.metrics import metrics


class ClusterObj: 

    """ This class describes a cluster

    Members:
    identifier: cluster id
    center: the mean of all cluster members
    closest_article: the member of cluster closest to the cluster center
    articles_list: list of article ids that belong to cluster

    """

    def __init__(self, identifier, center, spread_at_half, spread_at_full, closest_article, article_list):

        self.identifier = identifier
        self.center = center
        self.closest_article = closest_article
        self.article_list = article_list
        self.spread_at_half = spread_at_half
        self.spread_at_full = spread_at_full

    def __str__(self):
        return "<identifier: %s, center: %s, spread_at_half: %s, spread_at_full: %s, closest_article: %s, article_list: %s>\n" % (self.identifier, self.center, self.spread_at_half, self.spread_at_full, self.closest_article, self.article_list)    
      
             
def print_cluster_means(cluster_means, unique_tokens): 

    """ Given list of vectors and corresponding token list, prints the words in vector
    
    """

    for count, array in enumerate(cluster_means):
        indices = sorted(range(len(array)),key=lambda x:array[x])
        top_indices = indices[len(indices)-10:len(indices)]
        print count, " : ",
        for index in top_indices:
            print unique_tokens[index],
        print ""    


def cluster_articles(vectors, num_clusters, method):

    # cluster the article vectors
    if method == 'kmeans':
        assignment = cluster_kmeans(vectors, num_clusters, "cosine");
    elif method == 'gaac':
        assignment = cluster_gaac(vectors, num_clusters)
    elif method == 'nmf':
        assignment = cluster_nmf(vectors, num_clusters)

    return assignment
    

def get_cluster_objects(articles, assignment):

    num_clusters = set(assignment)

    cluster_obj_list = []

    for i in range(len(num_clusters)):

        # get articles in this cluster
        articles_in_cluster = [articles[count] for count, index in enumerate(assignment) if index == i ]

        # get the tfidf vectors for articles in this cluster
        vectors_in_cluster = [article.tfidf_vector for article in articles_in_cluster]

        # get the mean vector for this cluster
        cluster_mean = numpy.mean(vectors_in_cluster, axis=0)

        # find distance of each article in this cluster from the cluster mean
        distances = []
        for index, article in enumerate(articles_in_cluster):
            distances.append(math.sqrt(sum([math.pow(item[0]-item[1], 2) for item in zip(cluster_mean, article.tfidf_vector)])))
            article.distance_from_center = distances[index]
            article.cluster_id = i

        # find article closest to center
        closest_article_in_cluster = articles_in_cluster[distances.index(min(distances))]    

        # find spread at half and full
        distances.sort()
        half = int(len(distances)/2)
        spread_at_half = sum(distances[:half])/half
        spread_at_full = sum(distances)/len(distances)

        # create the cluster object
        cluster_obj_list.append(ClusterObj(i, cluster_mean, spread_at_half, spread_at_full, closest_article_in_cluster, articles_in_cluster)) 

    return cluster_obj_list

@metrics.inspect
@metrics.track    
def cluster(articles, params):
   
    # parse the parameters
    num_clusters = params.num_clusters
    clustering_method = params.clustering_method
    only_titles = params.only_titles	

    # convert articles to tf-idf vectors
    IDF, unique_tokens_dict, unique_tokens, vectors = vectorer.vectorize_articles(articles, only_titles)

    assignment = cluster_articles(vectors, num_clusters, clustering_method)
    #print assignment

    # get cluster objects
    clusters = get_cluster_objects(articles, assignment)

    return {'clusters': clusters, 'assignment': assignment}
