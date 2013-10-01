from __future__ import division
import opml
import nltk
from xml.dom.minidom import parse, parseString
import random
import re, pprint, numpy
from nltk.stem.wordnet import WordNetLemmatizer
import math
from nltk import cluster
from nltk.cluster import euclidean_distance, cosine_distance
import pickle
import os.path

# TO DO:
# 1) Give more weight to Nouns
# 2) Ignore numbers in text -- DONE
# 3) Add tech sites to stopword list
# 4) Try PCA/SVD

IDF = {} # to make script faster
unique_tokens_dict = {} # unique_token["token"] = id
unique_tokens = [] # unique_tokens[id] = "token"

class NewsItem: # class for each news item

    identifier = 0 # static id for each news item
    
    def __init__(self, title, feed_title, link, author, content, updated_at):
        
        self.title = title
        self.feed_title = feed_title
        self.link = link
        self.author = author
        self.content = content
        self.updated_at = updated_at
        self.id = self.identifier
        self.identifier = self.identifier + 1


def load_xml_data(file_name): # loads the opml file

    dom = parse(file_name) # parse an XML file by name

    itemlist = dom.getElementsByTagName('item') # get the items

    items = []

    for item in itemlist: # get the item contents
        
        try:

            title      =  item.getElementsByTagName('title')[0].firstChild.nodeValue
            feed_title =  item.getElementsByTagName('feed_title')[0].firstChild.nodeValue
            link       =  item.getElementsByTagName('link')[0].firstChild.nodeValue
            author     =  item.getElementsByTagName('author')[0].firstChild.nodeValue
            content    =  item.getElementsByTagName('content')[0].firstChild.nodeValue
            updated_at =  item.getElementsByTagName('updated_at')[0].firstChild.nodeValue

            items.append(NewsItem(title, feed_title, link, author, content, updated_at))

        except:
            pass

    return items

def tf(word, document, method = 'log'): # finds the term frequency of word in document

    if method == 'log':
        return math.log(document.count(word) + 1)
    if method == 'absolute':
        return document.count(word)


def tfidf(document): # creates the tf-idf vector using the global 'unique_tokens_dict'

    document = list(document)
    unique_text = set(document) # for iteration to create vector

    # our tfidf vector, initialized to zero
    word_tfidf = [0]*len(unique_tokens_dict) 

    # populate vector
    for word in unique_text: 
        index = unique_tokens_dict[word]
        word_tfidf[index] = tf(word, document, 'log') * IDF[word]
              
    return word_tfidf


def extend_stopwords(stopwords): # adds more stopwords as required

    stopwords.extend(['techcrunch', 'verge', 'allthingsd', 'engadget', 'gigaom', 'huffpost', 'wsj', 'bloomberg',
                      'businessweek', 'vogue', 'technica', '9to5mac', 'reuters', '9to5',
                      'cnet', 'zdnet', 'venturebeat', 'forbes', 
                      'anandtech', 'macrumors', 'dealbook', 'businessinsider', 'torrentfreak', 'ap',
                      'bgr', 'spiegel', 'citeworld', 'hillicon', '9to5google', 'techdirt', 'supersite',
                      'latimes', 'geekwire', 'fiercewireless', 'co.design', 'bbc', 'fireball', 'daring',
                      'pandodaily', 'usatoday', 'androidpolice', 'uncrunched', 'ifixit', 'appleinsider',
                      'slashgear', 'usatoday', 'techmeme', 'variety', 'ign', 'valleywag', 'readwrite',
                      'phonearena', 'newyorker', 'bizjournals', 'nakedsecurity', 'moneybeat', 'marco',
                      'techinasia', 'searchengineland', 'stratechery', 'tuaw', 'eurogamer', 'datacenterknowledge',
                      'moneybeat', 'agileblog', 'globeandmail', 'theregister', 'localytics', 'hollywoodreporter',
                      'theregister', 'pcworld', 'buzzfeed', 'firedoglake', 'laptopmag', 'hunterwalk', 'mashable',
                      'adage', 'adweek'])
    
    return stopwords


def cleanify_article(article): # converts article to tokens 

    # our stemmer 
    lmtzr = WordNetLemmatizer() 

    # list of stopwords
    stopwords = nltk.corpus.stopwords.words('english') 
    stopwords = extend_stopwords(stopwords)
    
    # tokenize article (makes list of words), make everything smallcaps, and lemmatize it (keeps only stems, eg: 'winning' to 'win')        
    tokens = [lmtzr.lemmatize(w.lower()) for w in nltk.word_tokenize(article.content.encode("utf-8"))]

    # removes tokens that are stopwords
    tokens = [token for token in tokens if token not in stopwords]
    
    # only keeps tokens of length greater than 2
    tokens = [token for token in tokens if len(token) > 2]

    # removes tokens that are numbers
    tokens = [token for token in tokens if not token.isdigit()]

    return tokens

def vectorize_articles(articles): # given a list of articles, converts to the tf-idf vector space

    global unique_tokens
    global unique_tokens_dict
    global IDF

    num_articles = len(articles)
    print "Num articles = ", num_articles

    # collection of all texts
    texts = [] 
    
    print "Generating tokens"
    for count, article in enumerate(articles):

        print count
        
        # get tokens from article
        tokens = cleanify_article(article)

        # generate bigrams
        #bi_tokens = nltk.bigrams(tokens)
        #tri_tokens = nltk.trigrams(tokens)
        #bi_tokens = [' '.join(token).lower() for token in bi_tokens]
        #bi_tokens = [token for token in bi_tokens if token not in stopwords]
        # generate trigrams
        #tri_tokens = [' '.join(token).lower() for token in tri_tokens]
        #tri_tokens = [token for token in tri_tokens if token not in stopwords]

        # collect all tokens
        final_tokens = []
        final_tokens.extend(tokens)
        #final_tokens.extend(bi_tokens)
        #final_tokens.extend(tri_tokens)

        text = nltk.Text(final_tokens) # create text from article
        texts.append(text) # add to collection of texts

        # make entry in IDF dictionary
        for token in set(final_tokens):
            if token not in IDF:
                IDF[token] = 1
            else:
                IDF[token] = IDF[token] + 1
    print "Finished generating tokens"

    # populate the Inverse Document Frequency
    print "Initializing IDF dictionary"
    for key in IDF:
        IDF[key] = math.log(num_articles/IDF[key])
    print "IDF dictionary ready for use"    
    
    # load the list of texts into a TextCollection object.
    collection = nltk.TextCollection(texts)
    print "Created a collection of", len(collection), "terms."

    # get a list of unique tokens, and recreate reverse dictionary
    unique_tokens = list(set(collection))
    count = 0
    for term in unique_tokens:
        unique_tokens_dict[term] = count
        count = count + 1
    print "Unique terms found: ", len(unique_tokens_dict)
    
    # And here we actually call the function and create our array of vectors.
    print "Creating vectors"
    vectors = []
    for count, text in enumerate(texts):
        print count
        vectors.append(numpy.array(tfidf(text)))
    print "Vectors created."
  
    return vectors


def print_cluster_means(cluster_means): # displays top words in each mean

    for count, array in enumerate(cluster_means):
        indices = sorted(range(len(array)),key=lambda x:array[x])
        top_indices = indices[len(indices)-10:len(indices)]
        print count, " : ",
        for index in top_indices:
            print unique_tokens[index],
            #print index
        print ""    
    
def cluster_articles(articles, method):

    # convert articles into tf-idf vectors
    #file_name = 'vectors.txt'
    #if os.path.exists(file_name):
    #    print "Loading previously saved vectors"
    #    fin = open(file_name, 'r')
    #    vectors = pickle.load(fin)
    #    fin.close()
    #else:
    #    vectors = vectorize_articles(articles)
    #    print "Saving vectors to file"
    #    fout = open(file_name, 'w')
    #    pickle.dump(vectors, fout)
    #    fout.close()

    vectors = vectorize_articles(articles)

    if method == 'kmeans':
        # initialise the kmeans clusterer
        clusterer = cluster.KMeansClusterer(10, cosine_distance)
        assignment = clusterer.cluster(vectors, False)
        cluster_means = clusterer.means()
        print_cluster_means(cluster_means)


    return None
    
if __name__ == "__main__":

    file_name = "../feeddumps/201309282106.opml"

    # get articles from wherever
    articles = load_xml_data(file_name)

    articles = articles[:200]

    # cluster the articles
    clusters = cluster_articles(articles, 'kmeans')







