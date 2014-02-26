from __future__ import division

import numpy, scipy, math
from datetime import datetime

import vectorer
import ranker
import clusterformats
from clustering_algos import *

from articurate.metrics import metrics
from articurate.utils.class_definitions import ClusterObj     
             
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
        avg_pairwise_dist = numpy.sum(avg_pairwise_dist_matrix) / (len(articles_in_cluster)*(len(articles_in_cluster)-1)/2 + 0.1)

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


def get_cluster_metrics(cluster_objects):

    """ Given a list of cluster objects, extracts metrics
    """

    for cluster in cluster_objects:

        # first metric: average pairwise distance for articles in cluster, already found

        # second metric: average number of named entities per title in cluster
        avg_num_ne = sum([article.num_ne for article in cluster.article_list]) / len(cluster.article_list)
        cluster.metrics['avg_named_entities'] = avg_num_ne

        # third metric: number of articles in cluster
        cluster.metrics['num_articles'] = len(cluster.article_list)

        # fourth metric: average publishing time of articles in cluster
        cluster_timestamps = [int(datetime.strptime(article.updated_at, '%Y-%m-%d %H:%M:%S').strftime('%s')) for article in cluster.article_list]
        avg_pub_time = sum(cluster_timestamps)/len(cluster_timestamps) 
        cluster.metrics['average_publishing_time'] = avg_pub_time

        # fifth metric: publishing time of newest article in cluster
        newest_pub_time = max(cluster_timestamps)
        cluster.metrics['newest_publishing_time'] = newest_pub_time    

        # sixth metric: publishing time of oldest article in cluster
        oldest_pub_time = min(cluster_timestamps)
        cluster.metrics['oldest_publishing_time'] = oldest_pub_time    


@metrics.track    
def cluster(articles, params):
   
    # parse the parameters
    num_clusters = params.num_clusters
    clustering_method = params.clustering_method
    only_titles = params.only_titles	

    # convert articles to tf-idf vectors
    IDF, unique_tokens_dict, unique_tokens, vectors = vectorer.vectorize_articles(articles, only_titles)

    # cluster the articles to get assignment
    assignment = cluster_articles(vectors, num_clusters, clustering_method)

    # create cluster objects from assignment
    cluster_objects = get_cluster_objects(articles, assignment)

    # derive metrics from cluster objects
    get_cluster_metrics(cluster_objects)

    # rank the cluster objects based on metrics
    cluster_objects = ranker.rank_clusters(cluster_objects)

    return {'clusters': cluster_objects, 'assignment': assignment}

    
