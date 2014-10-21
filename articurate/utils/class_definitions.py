class NewsItem: # class for each news item

    identifier = 0 # static id for each news item
    
    def __init__(self, title, feed_title, link, author, content, updated_at):
        
        # details from the internet
        self.title = title
        self.feed_title = feed_title
        self.link = link
        self.author = author
        self.content = content
        self.updated_at = updated_at

        # our representation
        self.tfidf_vector = []

        # our fields
        self.cluster_id = -1 # cluster id to which this item belongs
        self.distance_from_center = 0 # distance from cluster center
        self.id = self.identifier
        self.identifier = self.identifier + 1

        # extra metric fields
        self.num_ne = 0 # number of named entities
     


class ClusterObj: 

    """ This class describes a cluster

    Members:
    identifier: cluster id
    center: the mean of all cluster members
    closest_article: the member of cluster closest to the cluster center
    avg_pairwise_dist: average pairwise distance between articles in cluster
    article_list: list of article ids that belong to cluster
    NE_list: list of all named entities in cluster, sorted by frequency

    """

    def __init__(self, identifier, center, closest_article, article_list, NE):

        self.identifier = identifier
        self.center = center
        self.closest_article = closest_article
        self.article_list = article_list if len(article_list) > 0 else []
        self.NE_list = NE

        # metrics
        self.metrics = {}

    def __str__(self):
        return "<identifier: %s, center: %s, closest_article: %s, article_list: %s, NE_list: %s>\n" % (self.identifier, self.center, self.closest_article, self.article_list, self.NE_list)    
 
 
class ParamObj:

	""" Define parameters to use for clustering articles"""

	def __init__(self, num_clusters, clustering_method, only_titles):
		self.num_clusters = num_clusters
		self.clustering_method = clustering_method
		self.only_titles = only_titles


