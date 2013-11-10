"""Convert articles to tf-df vectors"""

from articurate.pymotherlode import api

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import math
import numpy
import json

IDF = {} # to make script faster
unique_tokens_dict = {} # unique_token["token"] = id
unique_tokens = [] # list of tokens


def tf(word, document, method = 'log'): # finds the term frequency of word in document

    if method == 'log':
        return math.log(document.count(word) + 1)
    if method == 'absolute':
        return document.count(word)


def tfidf(text, boost_ne): # creates the tf-idf vector using the global 'unique_tokens_dict'

    text = list(text)
    unique_text = set(text) # for iteration to create vector

    # our tfidf vector, initialized to zero
    word_tfidf = [0]*len(unique_tokens_dict) 

    # euclidean norm to divide by
    euclidean_norm = 0
   
    # default boost of one
    boost = 1

    if boost_ne:
        ne_dict = json.loads(api.getMetric("articurate.nertagger.celery_tasks.save_celery"))

    # populate vector
    for word in unique_text: 

        if boost_ne:
            # check if work in ne_dict
            if word in ne_dict['ORGANIZATION'] or word in ne_dict['LOCATION'] or word in ne_dict['PERSON']:
                boost = 2  # ne boost

        index = unique_tokens_dict[word]
        word_tfidf[index] = tf(word, text, 'log') * IDF[word] * boost
                
    # find the euclidean norm of the vector
    euclidean_norm = math.sqrt(sum([item*item for item in word_tfidf]))
      
    # normalize the tfidf vector
    word_tfidf = [item/euclidean_norm for item in word_tfidf]

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


def cleanify_text(text): # converts text to tokens 

    # our stemmer 
    lmtzr = WordNetLemmatizer() 

    # list of stopwords
    stopwords = nltk.corpus.stopwords.words('english') 
    stopwords = extend_stopwords(stopwords)
    
    # tokenize article (makes list of words), make everything smallcaps, and lemmatize it (keeps only stems, eg: 'winning' to 'win')        
    tokens = [lmtzr.lemmatize(w.lower()) for w in nltk.word_tokenize(text.encode("utf-8"))]

    # removes tokens that are stopwords
    tokens = [token for token in tokens if token not in stopwords]
    
    # only keeps tokens of length greater than 2
    tokens = [token for token in tokens if len(token) > 2]

    # removes tokens that are numbers
    tokens = [token for token in tokens if not token.isdigit()]

    return tokens


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


def vectorize_articles(articles, only_titles = True, truncate = False, boost_ne = True): # given a list of articles, converts to the tf-idf vector space

    global unique_tokens
    global unique_tokens_dict
    global IDF

    num_articles = len(articles)

    # collection of all texts and titles
    texts = [] 
    titles = []
    
    print "Generating tokens"
    for count, article in enumerate(articles):

        if count % 100 == 0:
            print count
        
        # get tokens from article
        tokens = cleanify_text(article.title) if only_titles == True else cleanify_text(article.content)
        
        # create text object from tokens and add to collection of texts
        texts.append(nltk.Text(tokens))

        # make entry in IDF dictionary
        for token in set(tokens):
            if token not in IDF:
                IDF[token] = 1
            else:
                IDF[token] = IDF[token] + 1
    print "Finished generating tokens\n"

    # populate the Inverse Document Frequency
    print "Initializing IDF dictionary"
    for key in IDF:
        IDF[key] = math.log(num_articles/IDF[key])
    print "IDF dictionary ready for use\n"    
    
    # convert tokens to collection object
    collection = nltk.TextCollection(texts)
    print "Created a collection of", len(collection), "terms."

    # get a list of unique tokens, and recreate reverse dictionary
    unique_tokens = list(set(collection))
    count = 0
    for term in unique_tokens:
        unique_tokens_dict[term] = count
        count = count + 1
    print "Unique terms found: ", len(unique_tokens_dict), "\n"
    
    # And here we actually call the function and create our array of vectors.
    print "Creating vectors"
    vectors = []

    for count, item in enumerate(texts):
        
        if count % 100 == 0:
            print count
        
        # get the tfidf vector
        tfidf_vector = tfidf(item, boost_ne) 
        articles[count].tfidf_vector = tfidf_vector # insert in article object
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

       
