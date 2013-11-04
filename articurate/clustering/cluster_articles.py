from __future__ import division
import re, pprint, numpy
import time

from nltk import cluster
from nltk.cluster import euclidean_distance, cosine_distance
from scipy import spatial
from scipy.sparse import csr_matrix
import fastcluster
import nimfa

from articurate.pymotherlode.api import *
import articurate.utils.loader as loader

import vectorer
import clusterformats
from clustering_algos import *

# TO DO:
# 1) Give more weight to Nouns

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

    cluster_means = []

    for i in range(0, num_labels):
        
        indices = [j for j in range(len(assignment)) if assignment[j] == i]

        print i, indices

        cluster_vectors = numpy.array([vectors[j] for j in indices])

        print numpy.mean(cluster_vectors, axis=0)
        cluster_means.append(numpy.mean(cluster_vectors, axis=0))

    return cluster_means
    
def cluster_articles(vectors, num_clusters, method):

    # cluster the input vectors
    if method == 'kmeans':
        assignment = cluster_kmeans(vectors, num_clusters, "cosine");
    elif method == 'gaac':
        assignment = cluster_gaac(vectors, num_clusters)
    elif method == 'nmf':
        assignment = cluster_nmf(vectors, num_clusters)

    return assignment
    
if __name__ == "__main__":

    # get articles from wherever
    articles = loader.get_latest_dump()
	
    # convert articles to tf-idf vectors
    IDF, unique_tokens_dict, unique_tokens, vectors = vectorer.vectorize_articles(articles, only_titles = True)

    # cluster the articles
    num_clusters = 10

    assignment = cluster_articles(vectors, num_clusters, 'nmf')
    #print assignment

    #Stores a copy of the cluster in JSON in the motherlode, with or without content
    clusterformats.clustersToJSON(articles, assignment)








