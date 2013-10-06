from __future__ import division
import re, pprint, numpy
import time
import math

from nltk import cluster
from nltk.cluster import euclidean_distance, cosine_distance
from scipy import spatial
from scipy.sparse import csr_matrix
import fastcluster
import nimfa

import vectorer
import clusterformats

# TO DO:
# 1) Give more weight to Noun
# 4) Try PCA/SVD/NMF

class ClusterObj: # class for each cluster

    def __init__(self, identifier, center, spread_at_half, spread_at_full, closest_article, article_list):

        self.identifier = identifier
        self.center = center
        self.spread_at_half = spread_at_half
        self.spread_at_full = spread_at_full
        self.closest_article = closest_article
        self.article_list = article_list
      
      
       
def print_cluster_means(cluster_means, unique_tokens): # displays top words in each mean

    for count, array in enumerate(cluster_means):
        indices = sorted(range(len(array)),key=lambda x:array[x])
        top_indices = indices[len(indices)-10:len(indices)]
        print count, " : ",
        for index in top_indices:
            print unique_tokens[index],
        print ""    

def cluster_means_from_assignment(vectors, assignment):

    num_labels = len(set(assignment))

    print assignment

    cluster_means = []

    for i in range(0, num_labels):
        
        indices = [j for j in range(len(assignment)) if assignment[j] == i]

        print i, indices

        cluster_vectors = numpy.array([vectors[j] for j in indices])

        print numpy.mean(cluster_vectors, axis=0)
        cluster_means.append(numpy.mean(cluster_vectors, axis=0))

    return cluster_means
        

def cluster_nmf(vectors, rank):

    print "Starting NMF clustering"
 
    start_time = time.time()
    
    # Run NMF.
    # Change this later and see which is best
    vectors_matrix = numpy.matrix(vectors)
    vectors_matrix = vectors_matrix.transpose()
    
    # Generate random matrix factors which we will pass as fixed factors to Nimfa.
    init_W = numpy.random.rand(vectors_matrix.shape[0], rank)
    init_H = numpy.random.rand(rank, vectors_matrix.shape[1])

    fctr = nimfa.mf(vectors_matrix, method = "nmf", seed = "fixed", W = init_W, H = init_H, rank = rank)
    fctr_res = nimfa.mf_run(fctr)

    # Basis matrix
    W = fctr_res.basis()

    # Mixture matrix
    H = fctr_res.coef()

    # get assignments
    assignment = []
    for index in range(H.shape[1]):
        column = list(H[:, index])
        assignment.append(column.index(max(column)))

    # Print the loss function (Euclidean distance between target matrix and its estimate). 
    print "Euclidean distance: %5.3e" % fctr_res.distance(metric = "euclidean")

    end_time = time.time()
    print "Clustering required", (end_time-start_time),"seconds"

    return assignment


def cluster_kmeans(vectors, num_clusters, distance_metric):

    print "Starting KMeans clustering"
    
    start_time = time.time()

    # initialize
    if distance_metric == "euclidean":
        clusterer = cluster.KMeansClusterer(num_clusters, euclidean_distance)
    elif distance_metric == "cosine":
        clusterer = cluster.KMeansClusterer(num_clusters, cosine_distance)

    assignment = clusterer.cluster(vectors, True)
    
    end_time = time.time()
    print "Clustering required", (end_time-start_time),"seconds"

    return assignment


def cluster_gaac(vectors, num_clusters):

    print "Starting GAAC clustering"
    
    start_time = time.time()

##    # nltk implementation might not be that good
##    clusterer = cluster.GAAClusterer(num_clusters)
##    assignment = clusterer.cluster(vectors, True)

    distance = spatial.distance.pdist(vectors, 'cosine')

    linkage = fastcluster.linkage(distance,method="complete")

    clustdict = {i:[i] for i in xrange(len(linkage)+1)}
    for i in xrange(len(linkage)-num_clusters+1):
        clust1= int(linkage[i][0])
        clust2= int(linkage[i][1])
        clustdict[max(clustdict)+1] = clustdict[clust1] + clustdict[clust2]
        del clustdict[clust1], clustdict[clust2]

    # generate the assignment list (vector -> cluster id)
    assignment = [-1]*len(vectors)

    count = 0
    for key in clustdict:
        value = clustdict[key]
        for item in value:
            assignment[item] = count
        count = count + 1

    end_time = time.time()
    print "Clustering required", (end_time-start_time),"seconds"

    return assignment
    
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
    

def cluster(articles, params):
   
    # parse the parameters
    num_clusters = params.num_clusters
    method = params.clustering_method

    # convert articles to tf-idf vectors
    IDF, unique_tokens_dict, unique_tokens, vectors = vectorer.vectorize_articles(articles)

    # reduce dimension of vectors
    #reduced_dim = 100
    #truncated_vectors = vectorer.truncated_SVD_vector(full_vectors, reduced_dim)

    #assignment = cluster_articles(vectors, num_clusters, 'gaac')
    #print assignment
    #print_cluster_means(cluster_means, unique_tokens)

    #assignment = cluster_articles(vectors, num_clusters, 'kmeans')
    #print assignment
    #print_cluster_means(cluster_means, unique_tokens)

    assignment = cluster_articles(vectors, num_clusters, method)
    #print assignment

    # get cluster objects
    clusters = get_cluster_objects(articles, assignment)

    return {'clusters': clusters, 'assignment': assignment}
