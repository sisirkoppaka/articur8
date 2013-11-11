from __future__ import division

import numpy, scipy
import time
import math
from sklearn.cluster import DBSCAN

from nltk import cluster
from nltk.cluster import euclidean_distance, cosine_distance
from scipy import spatial
from scipy.sparse import csr_matrix
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist
import fastcluster

import nimfa


def cluster_nmf(vectors, rank):

    """ Takes in vectors and clusters them using Non Negative Matrix Factorization.

    Inputs:
    vectors -- matrix containing rows of vectors
    rank -- number of clusters to create

    """

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


def cluster_kmeans(vectors, num_clusters, distance_metric = "cosine"):


    """ Takes in vectors and clusters them using KMeans clustering.

    Inputs:
    vectors -- matrix containing rows of vectors
    num_clusters -- number of clusters to create
    distance_metric -- distance measure between vectors (default "cosine")

    """

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


    """ Takes in vectors and clusters them using Group Average Agglomerative clustering with cosine distance.

    Inputs:
    vectors -- matrix containing rows of vectors
    num_clusters -- number of clusters to create

    """

    print "Starting GAAC clustering"
    
    start_time = time.time()

    # doesnt work :: try scipy clustering with threshold
    #assignment = hier.fcluster(numpy.clip(fastcluster.linkage(vectors, method='complete', metric='cosine'), 0, 1), 0.2, criterion='distance')


    # nltk implementation might not be that good
    #clusterer = cluster.GAAClusterer(num_clusters)
    #assignment = clusterer.cluster(vectors, True)

    distance = spatial.distance.pdist(vectors, 'cosine')

    linkage = fastcluster.linkage(distance,method="complete")
    
    # try DBSCAN
    #db = DBSCAN(eps=0.01, min_samples=5).fit(spatial.distance.squareform(distance))
    #labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    #n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    #print 'Estimated number of clusters: %d' % n_clusters_


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
