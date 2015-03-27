import math
import time

def rank_clusters(cluster_objects):

    """ Given a list of cluster objects, ranks them according to learnt function """

    # now sort them
    sorted_clusters = sorted(cluster_objects, key = lambda cluster : rank_formula(cluster), reverse = True)

    for cluster in sorted_clusters:
    	cluster.metrics['score'] = rank_formula(cluster)

    return sorted_clusters

# rank_clusters() ends


def rank_formula(cluster):

	""" Our formula to score each cluster """

	# avg_named_entities
	# oldest_publishing_time
	# num_articles
	# newest_publishing_time
	# avg_distance_from_center
	# average_publishing_time

  	# get current time
  	current_time   = int(time.time())
	named_entities = math.log(1.1 + cluster.metrics['avg_named_entities'])
	cluster_size   = math.log(cluster.metrics['num_articles'])
	spread         = math.exp(cluster.metrics['avg_distance_from_center']*10+0.1)
	time_decay     = math.exp(cluster.metrics['average_publishing_time'] / current_time);

	
	if cluster.metrics['num_articles'] == 1:
		return 0
	else:
		return named_entities * cluster_size / spread * time_decay
	
	#value3 = cluster.metrics['avg_distance_from_center']*10+0.1
	#return math.log(cluster.metrics['avg_named_entities'] + 2) * math.log(cluster.metrics['num_articles'] + 1) / (cluster.metrics['avg_pairwise_dist']+0.5)
	#return  1/(cluster.metrics['avg_pairwise_dist']+0.5)
