"""Convert articles to tf-df vectors"""

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import math
import numpy
import json

from articurate.pymotherlode import api
from articurate.metrics import metrics
from articurate.pymotherlode.api import *
from articurate.utils.config import *


DF = {} # to make script faster
IDF = {} # to make script faster
unique_tokens_dict = {} # unique_token["token"] = id
unique_tokens = [] # list of tokens

def truncated_SVD_vector(vectors, reduced_dim): # transforms input vectors to lower dimensions using SVD of reduced dim

    U, S, V = numpy.linalg.svd(vectors, full_matrices=False)

    print U.shape, S.shape, V.shape

    newU = U[:, :reduced_dim]
    newS = S[:reduced_dim]
    newV = V[:reduced_dim, :]

    print newU.shape, newS.shape, newV.shape

    diagS = numpy.zeros((reduced_dim, reduced_dim))
    diagS[:, :] = numpy.diag(newS)

    truncated_vectors = numpy.dot(newU, numpy.dot(diagS, newV))

    print numpy.allclose(vectors, truncated_vectors)
                               
    dummy = raw_input()
    
    return truncated_vectors

# truncated_SVD_vector() ends

def tf(word, document, method = 'log'): # finds the term frequency of word in document

    if method == 'log':
        return math.log(document.count(word) + 1)
    if method == 'absolute':
        return document.count(word)


def tfidf(text, boost_ne, ne_dict = {}): # creates the tf-idf vector using the global 'unique_tokens_dict'

    text = list(text)
    unique_text = set(text) # for iteration to create vector

    # our tfidf vector, initialized to zero
    word_tfidf = [0]*len(unique_tokens_dict) 

    # euclidean norm to divide by
    euclidean_norm = 0
   
    # default boost of one
    boost = 1
    num_ne = 0        
    named_entities = []

    # populate vector
    for word in unique_text: 
        if word in unique_tokens_dict:
            if boost_ne:
                # check if work in ne_dict
                if word in ne_dict['ORGANIZATION'] or word in ne_dict['LOCATION'] or word in ne_dict['PERSON']:
                    boost = 1.2  # ne boost
                    num_ne = num_ne + 1 # increse number of named entities found
                    named_entities.append(word)


            index = unique_tokens_dict[word]
            word_tfidf[index] = tf(word, text, 'log') * IDF[word] * boost
                
    # find the euclidean norm of the vector
    euclidean_norm = math.sqrt(sum([item*item for item in word_tfidf]))
      
    # normalize the tfidf vector
    word_tfidf = [item/(euclidean_norm+0.0001) for item in word_tfidf]

    return {'tfidf_vector': word_tfidf, 'num_ne': num_ne, 'named_entities': named_entities}


def extend_stopwords(stopwords, area): # adds more stopwords as required

    if area == 'tech':
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

@metrics.track_by("tech")
def get_stopwords():
    
    # list of stopwords
    stopwords = nltk.corpus.stopwords.words('english') 
    stopwords = extend_stopwords(stopwords, 'tech')
    return stopwords


def cleanify_text(text, stopwords, ne_dict = {}): # converts text to tokens 

    # our stemmer 
    lmtzr = WordNetLemmatizer() 
    
    # tokenize article (makes list of words), make everything smallcaps, and lemmatize it (keeps only stems, eg: 'winning' to 'win')        
    # unless the token is a named entity, in which case keep it as it is
    tokens = []
    for w in nltk.word_tokenize(text.encode("utf-8")):
        w = w.lower()
        if w in ne_dict['ORGANIZATION'] or w in ne_dict['LOCATION'] or w in ne_dict['PERSON']:
            tokens.append(w)
        else:
            tokens.append(lmtzr.lemmatize(w))
    
    #tokens = [lmtzr.lemmatize(w.lower()) for w in nltk.word_tokenize(text.encode("utf-8"))]

    # removes tokens that are stopwords
    tokens = [token for token in tokens if token not in stopwords]
    
    # only keeps tokens of length greater than 2
    tokens = [token for token in tokens if len(token) > 2]

    # removes tokens that are numbers
    tokens = [token for token in tokens if not token.isdigit()]

    return tokens


def vectorize_articles(articles, only_titles = True, use_SVD = False, boost_ne = True): # given a list of articles, converts to the tf-idf vector space

    global unique_tokens
    global unique_tokens_dict
    global IDF

    num_articles = len(articles)

    # collection of all texts and titles
    texts = [] 
    titles = []
    
    # get the NER list
    try: 
        ne_dict = json.loads(api.getMetric("articurate.nertagger.celery_tasks.save_celery")) if boost_ne else {}
    except:
        ne_dict = {"LOCATION":{}, "PERSON":{}, "ORGANIZATION":{}}

    print ne_dict["ORGANIZATION"]
    print ne_dict["LOCATION"]
    print ne_dict["PERSON"]

    # get the stopword list
    if config['db.coldStart']: # do this for storing it first time in DB
        stopwords = get_stopwords()
    else: # do this for retrieving from DB henceforth
        stopwords = getMetricByKey("articurate.clustering.vectorer.get_stopwords", "tech")

    print "Generating tokens"
    for count, article in enumerate(articles):

        if count % 100 == 0:
            print count
        
        # get tokens from article
        tokens = cleanify_text(article.title, stopwords, ne_dict) if only_titles == True else cleanify_text(article.content, stopwords, ne_dict)
        
        # create text object from tokens and add to collection of texts
        texts.append(nltk.Text(tokens))

        # make entry in IDF dictionary
        for token in set(tokens):
            if token not in DF:
                DF[token] = 1
            else:
                DF[token] = DF[token] + 1
    print "Finished generating tokens\n"

    # populate the Inverse Document Frequency
    print "Initializing IDF dictionary"
    for key in DF:
        IDF[key] = math.log(num_articles/DF[key])
    print "IDF dictionary ready for use\n"    
    
    # convert tokens to collection object
    collection = nltk.TextCollection(texts)
    print "Created a collection of", len(collection), "terms."

    # get a list of unique tokens, and recreate reverse dictionary
    unique_tokens = list(set(collection))
    # # crop unique tokens
    # cropped_unique_tokens = []
    # for term in unique_tokens:
    #     if DF[term] > 1:
    #         print term, DF[term]
    #         cropped_unique_tokens.append(term)
    # unique_tokens = cropped_unique_tokens

    for count, term in enumerate(unique_tokens):
        unique_tokens_dict[term] = count
    print "Unique terms found: ", len(unique_tokens_dict), "\n"
    
    # And here we actually call the function and create our array of vectors.
    print "Creating vectors"
    vectors = []

    for count, item in enumerate(texts):
        
        if count % 100 == 0:
            print count
        
        # get the tfidf vector
        tfidf_info = tfidf(item, boost_ne, ne_dict) 
        tfidf_vector = tfidf_info['tfidf_vector']
        articles[count].tfidf_vector   = tfidf_vector # insert in article object
        articles[count].num_ne         = tfidf_info['num_ne'] # insert number of named entities in article object
        articles[count].named_entities = tfidf_info['named_entities']
        vectors.append(numpy.array(tfidf_vector))
    print "Vectors created\n"

    return IDF, unique_tokens_dict, unique_tokens, vectors


# SCRATCH
 
        # generate bigrams
        #bi_tokens = nltk.bigrams(tokens)
        #tri_tokens = nltk.trigrams(tokens)
        #bi_tokens = [' '.join(token).lower() for token in bi_tokens]
        #bi_tokens = [token for token in bi_tokens if token not in stopwords]
        # generate trigrams
        #tri_tokens = [' '.join(token).lower() for token in tri_tokens]
        #tri_tokens = [token for token in tri_tokens if token not in stopwords]

       
