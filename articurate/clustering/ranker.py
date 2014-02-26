def rank_clusters(cluster_objects):

    """ Given a list of cluster objects, ranks them according to learnt function
    """

    # now sort them
    sorted_clusters = sorted(cluster_objects, key = lambda cluster : rank_formula(cluster))
    return sorted_clusters



def rank_formula(cluster):
	
	""" Our formula to score each cluster """

	return cluster.metrics['avg_pairwise_dist']