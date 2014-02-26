def rank_clusters(cluster_objects):

    """ Given a list of cluster objects, ranks them according to learnt function
    """

    # now sort them
    sorted_clusters = sorted(cluster_objects, key = lambda cluster: cluster.metrics[cluster.metric_names.index('avg_pairwise_dist')])
    return sorted_clusters

