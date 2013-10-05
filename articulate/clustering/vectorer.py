"""Convert articles to tf-df vectors"""

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import math
import numpy

IDF = {} # to make script faster
unique_tokens_dict = {} # unique_token["token"] = id
unique_tokens = [] # list of tokens


def tf(word, document, method = 'log'): # finds the term frequency of word in document

    if method == 'log':
        return math.log(document.count(word) + 1)
    if method == 'absolute':
        return document.count(word)


def tfidf(document, title, boost_title=False): # creates the tf-idf vector using the global 'unique_tokens_dict'

    document = list(document)
    unique_text = set(document) # for iteration to create vector

    # our tfidf vector, initialized to zero
    word_tfidf = [0]*len(unique_tokens_dict) 

    # euclidean norm to divide by
    euclidean_norm = 0
  
    # populate vector
    for word in unique_text: 
        index = unique_tokens_dict[word]
        word_tfidf[index] = tf(word, document, 'log') * IDF[word]
            
    # boost words in title
    if boost_title == True:
        for word in title:
            if word in unique_tokens:
                index = unique_tokens_dict[word]
                word_tfidf[index] = word_tfidf[index]*2 
     
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

def vectorize_articles(articles, truncate = False): # given a list of articles, converts to the tf-idf vector space

    global unique_tokens
    global unique_tokens_dict
    global IDF

    num_articles = len(articles)

    # collection of all texts and titles
    texts = [] 
    titles = []
    
    print "Generating tokens"
    for count, article in enumerate(articles):

        print count
        
        # get tokens from article
        tokens = cleanify_text(article.content)
        title = cleanify_text(article.title)

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

        title = nltk.Text(title)
        titles.append(title)

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
    
    # load the list of texts and titles into a TextCollection object.
    #all_text = texts
    #all_text.extend(titles)
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
    for count, item in enumerate(zip(texts, titles)):
        print count
        vectors.append(numpy.array(tfidf(item[0], item[1], boost_title = False)))
    print "Vectors created\n"

    return IDF, unique_tokens_dict, unique_tokens, vectors



        
