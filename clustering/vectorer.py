"""Convert articles to tf-df vectors"""

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import math
import numpy

IDF = {} # to make script faster
unique_tokens_dict = {} # unique_token["token"] = id
unique_tokens = [] # unique_tokens[id] = "token"


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
    print "Finished generating tokens\n"

    # populate the Inverse Document Frequency
    print "Initializing IDF dictionary"
    for key in IDF:
        IDF[key] = math.log(num_articles/IDF[key])
    print "IDF dictionary ready for use\n"    
    
    # load the list of texts into a TextCollection object.
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
    for count, text in enumerate(texts):
        print count
        vectors.append(numpy.array(tfidf(text)))
    print "Vectors created\n"
  
    return IDF, unique_tokens_dict, unique_tokens, vectors