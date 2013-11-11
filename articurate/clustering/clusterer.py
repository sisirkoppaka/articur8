from __future__ import division

import numpy, scipy

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
    avg_pairwise_dist: average pairwise distance between articles in cluster
    articles_list: list of article ids that belong to cluster

    """

    def __init__(self, identifier, center, avg_pairwise_dist, closest_article, article_list):

        self.identifier = identifier
        self.center = center
        self.closest_article = closest_article
        self.article_list = article_list
        self.avg_pairwise_dist = avg_pairwise_dist

    def __str__(self):
        return "<identifier: %s, center: %s, closest_article: %s, avg_pairwise_dist: %s, article_list: %s>\n" % (self.identifier, self.center, self.closest_article, self.avg_pairwise_dist, self.article_list)    
      
             
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
        if len(distances) > 0:
            closest_article_in_cluster = articles_in_cluster[distances.index(min(distances))]    
        else:
            closest_article_in_cluster = None

        # find average pairwise distance of articles in cluster    
        avg_pairwise_dist_matrix = scipy.spatial.distance.pdist(vectors_in_cluster)
        avg_pairwise_dist = numpy.sum(avg_pairwise_dist_matrix)

        # # find spread at half and full
        # distances.sort()
        # half = int(len(distances)/2)
        # #spread_at_half = sum(distances[:half])/half
        # #spread_at_full = sum(distances)/len(distances)
        # spread_at_half = 0
        # spread_at_full = 0

        # create the cluster object
        cluster_obj_list.append(ClusterObj(i, cluster_mean, avg_pairwise_dist, closest_article_in_cluster, articles_in_cluster)) 

    return cluster_obj_list


def rank_cluster_objects(cluster_objects, articles):

    """ Given a list of cluster objects, ranks them according to different metrics

    """

    # first metric: get the average pairwise distance for articles in cluster
    # rank in ascending order of values
    for cluster in cluster_objects:
        print cluster.identifier, cluster.avg_pairwise_dist

    print "\n\nsorting now\n\n"

    # now sort them
    sorted_clusters = sorted(cluster_objects, key = lambda cluster: cluster.avg_pairwise_dist)

    for cluster in sorted_clusters:
        print cluster.identifier, cluster.avg_pairwise_dist    

    return sorted_clusters

#@metrics.inspect
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

    # rank cluster objects
    clusters = rank_cluster_objects(clusters, articles)

    return {'clusters': clusters, 'assignment': assignment}

    
