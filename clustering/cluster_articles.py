from __future__ import division
import opml
import nltk
from xml.dom.minidom import parse, parseString
import random
import re, pprint, numpy
from nltk.stem.wordnet import WordNetLemmatizer
import math

IDF = {} # to make script faster
unique_tokens_dict = {} # unique_token["token"] = id

class NewsItem: # class for each news item

    identifier = 0
    
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


# Function to create a TF*IDF vector for one document.  For each of
# our unique words, we have a feature which is the td*idf for that word
# in the current document
def TFIDF(text):

    unique_text = set(list(text)) # for iteration to create vector
    text = list(text)
    
    word_tfidf = [0]*len(unique_tokens_dict) # our vector, initialized to zero

    #print "Num words = ", len(text), " Num unique words = ", len(unique_text)

    for word in unique_text: # populate vector
        index = unique_tokens_dict[word]
        word_tfidf[index] = math.log(text.count(word) + 1) * IDF[word]
              
    return word_tfidf


def vectorize_articles(articles):

    num_articles = len(articles)

    print "Num articles = ", num_articles

    texts = [] # collection of all texts
    lmtzr = WordNetLemmatizer() # our stemmer 
    stopwords = nltk.corpus.stopwords.words('english') # list of stopwords

    print "Generating tokens"
    count = 1

    for item in articles:

        print count
        count = count + 1
        
        tokens = [lmtzr.lemmatize(w.lower()) for w in nltk.word_tokenize(item.content.encode("utf-8"))]

        #bi_tokens = nltk.bigrams(tokens)
        #tri_tokens = nltk.trigrams(tokens)

        # keep tokens of length greater than 2
        tokens = [token for token in tokens if len(token) > 2 and token not in stopwords]

        # generate bigrams
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

        text = nltk.Text(final_tokens)
        texts.append(text)

        # make entry in IDF dictionary
        for token in set(final_tokens):
            if token not in IDF:
                IDF[token] = 1
            else:
                IDF[token] = IDF[token] + 1
            

    print "Finished generating tokens\nInitializing IDF dictionary"
    for key in IDF:
        IDF[key] = math.log(num_articles/IDF[key])

    print "IDF dictionary ready for use"    
    
    # load the list of texts into a TextCollection object.
    collection = nltk.TextCollection(texts)
    print "Created a collection of", len(collection), "terms."

    # get a list of unique tokens
    unique_tokens = list(set(collection))
    count = 0
    for term in unique_tokens:
        unique_tokens_dict[term] = count
        count = count + 1
    print "Unique terms found: ", len(unique_tokens_dict)

    print "Creating vectors"
    # And here we actually call the function and create our array of vectors.
    vectors = []
    count = 0
    for text in texts:
        print count
        count = count + 1
        vectors.append(numpy.array(TFIDF(text)))

    #vectors = [numpy.array(TFIDF(f, unique_terms, )) for f in texts]
    print "Vectors created."
    #print "First 10 words are", unique_tokens[:10]
    #print "First 10 stats for first document are", vectors[0][0:10]
  

    #for item in texts[0]:
    #    print item

    return vectors

    
def cluster_articles(articles, method):

    # convert articles into tf-idf vectors
    
    vectors = vectorize_articles(articles)

    return None
    
if __name__ == "__main__":

    file_name = "../feeddumps/201309282106.opml"

    articles = load_xml_data(file_name)

    #articles = articles[:100]

    clusters = cluster_articles(articles, 'kmeans')







