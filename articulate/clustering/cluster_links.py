from linkgraph import Article, Referral
from bulbs.neo4jserver import Graph

def add_referral(g, fromURL, toURL):
	#Lookup index of fromURL, which we know should exist in g
	fromNode = g.article.index.lookup(url = fromURL)
	#Check if toURL exists in g, add if it doesn't
	toNode = g.vertices.index.lookup(url = toURL)
	if len(list(toNode))==0:
		add_article(g, toURL)
		toNode = g.vertices.index.lookup(url = toURL)
		#Create referral
		g.referral.create(fromNode,toNode)
	else:
		#toURL exists in g, so just add the referral
		toNode = g.vertices.index.lookup(url = toURL)
		#Create referral
		g.referral.create(fromNode,toNode)		

def add_article(g, URL):
	g.article.create(url = URL)

def initialize():
	#Make sure you have done a neo4j start before this
	g = Graph() # uses default server address to connect
	g.add_proxy("article", Article)
	g.add_proxy("referral", Referral)

	return g

