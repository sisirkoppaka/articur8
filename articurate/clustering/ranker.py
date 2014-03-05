import math

def rank_clusters(cluster_objects):

    """ Given a list of cluster objects, ranks them according to learnt function
    """

    # now sort them
    sorted_clusters = sorted(cluster_objects, key = lambda cluster : rank_formula(cluster), reverse = True)
    return sorted_clusters



def rank_formula(cluster):
	
	""" Our formula to score each cluster """

	# avg_named_entities
	# oldest_publishing_time
	# num_articles
	# newest_publishing_time
	# avg_pairwise_dist
	# average_publishing_time

	return math.log(cluster.metrics['avg_named_entities'] + 2) * math.log(cluster.metrics['num_articles'] + 1) / (cluster.metrics['avg_pairwise_dist']+0.5)
	#return  1/(cluster.metrics['avg_pairwise_dist']+0.5)