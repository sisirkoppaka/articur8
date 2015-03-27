from __future__ import division

import numpy, scipy, math
from datetime import datetime
from scipy.spatial.distance import cosine as scipy_cos_dist
import itertools

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

        # get the named entities in this cluster
        named_entities = []
        for article in articles_in_cluster:
            named_entities.extend(article.named_entities)
        NE = list(set(named_entities))
        NE.sort(key = lambda x:named_entities.count(x))
        cropped_NE = []
        for item in NE:
            if named_entities.count(item) >= len(articles_in_cluster) * 0.75:
                cropped_NE.append(item)

        print NE, cropped_NE
        NE = cropped_NE

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

        # create the cluster object
        cluster_obj_list.append(ClusterObj(i, cluster_mean, closest_article_in_cluster, articles_in_cluster, NE))

    return cluster_obj_list


def get_cluster_metrics(cluster_objects):

    """ Given a list of cluster objects, extracts metrics
    """

    for cluster in cluster_objects:

        # first metric: average distance from center
        #center = cluster.center
        center = cluster.closest_article.tfidf_vector
        avg_distance_from_center = sum([scipy_cos_dist(article.tfidf_vector, center) for article in cluster.article_list]) / len(cluster.article_list)
        cluster.metrics['avg_distance_from_center'] = avg_distance_from_center

        # second metric: average number of named entities per title in cluster
        #avg_num_ne = sum([article.num_ne for article in cluster.article_list]) / len(cluster.article_list)
        cluster.metrics['avg_named_entities'] = len(cluster.NE_list)

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


def remove_duplicate_clusters(clusters, closeness_threshold = 0.75):

    # indices of clusters to be kept for sure and ignored for sure
    ignored_list = []
    keep_list = []

    # compute distance between clusters
    vectors = [cluster.closest_article.tfidf_vector for cluster in clusters]
    distance = spatial.distance.pdist(vectors, 'cosine')

    # sort according to distance, closest first
    sorted_distances = sorted(distance)
    sorted_order = [i[0] for i in sorted(enumerate(distance), key=lambda x:x[1])]

    indices = list(itertools.combinations(range(len(vectors)),2))

    # time to compare and keep/ignore what's to be kept/ignored
    for index, item in enumerate(sorted_order):

        i = indices[item][0]
        j = indices[item][1]

        if sorted_distances[index] <= closeness_threshold:

            # time to remove one of the clusters
            # keep the one that would be ranked higher
            if i < j:
                to_keep = i
                to_ignore = j
            else:
                to_keep = j
                to_ignore = i

            ignored_list.append(to_ignore)

            if to_keep not in ignored_list: # keep only if not previously ignored when compared to even higher ranked cluster
                keep_list.append(to_keep)

            #else:
            #    print "Previously ignored:: ", clusters[to_keep].closest_article.title
            #print sorted_distances[index]
            #print clusters[to_keep].closest_article.title
            #print "Ignoring:: ", clusters[to_ignore].closest_article.title
            #print "\n\n"

        else:
            break

    # remove stuff that might have been ignored but was in keep_list (for cyclic cases?)
    # this might be useless
    ignored_list = [index for index in ignored_list if index not in keep_list]

    # return stuff that won
    output_clusters = [clusters[index] for index in range(len(clusters)) if index not in ignored_list]

    return output_clusters


def find_robust_clusters(result):

    clusters = {}
    clusters['nmf'] = result['nmf']['clusters']
    clusters['gaac'] = result['gaac']['clusters']

    # nmf across height, gaac across width
    h = len(clusters['nmf'])
    w = len(clusters['gaac'])

    print h, w

    # time to compare each pair of clusters
    difference_list = [] # (i, j, {(in i, not in j) + (in j, not in i)} / (m+n))

    indices = list(itertools.combinations(range(max(h, w)),2))
    for index in indices:
        if index[0] < h: # take only the valid ones

            i = index[0]
            j = index[1]

            in_i = clusters['nmf'][i].article_list
            in_j = clusters['gaac'][j].article_list

            in_i_not_j = sum([1 for item in in_i if item not in in_j])
            in_j_not_i = sum([1 for item in in_j if item not in in_i])

            set_diff_value = (in_i_not_j + in_j_not_i) / (len(in_i) + len(in_j))

            difference_list.append((i, j, set_diff_value))

    sorted_diff = sorted(difference_list, key=lambda x:x[2])

    for i in range(0, 10):
        print sorted_diff[i][2]

        for item in clusters['nmf'][sorted_diff[i][0]].article_list:
            print item.title

        print "-------"

        for item in clusters['gaac'][sorted_diff[i][1]].article_list:
            print item.title

        print "\n\n"

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

    # remove duplicate clusters
    cluster_objects = remove_duplicate_clusters(cluster_objects)

    return {'clusters': cluster_objects, 'assignment': assignment}

    # find robust clusters, supported by both clustering methods
    #result['combined'] = clusterer.find_robust_clusters(result)
