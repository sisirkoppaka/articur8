from bs4 import BeautifulSoup
from urlparse import urlparse
import requests
import re
import feedfinder 
import time
import pickle
import os.path
import sys

def get_feeds(old_links, url):

    r  = requests.get(url)

    data = r.text
    soup = BeautifulSoup(data)

    news_source_list  = []
    twitter_feed_list = []

    for link in soup.find_all('a'):
        
        full_link = link.get('href')

        try:

            o = urlparse(full_link)
            news_source = o.hostname 

            if news_source is None:
                continue

            if news_source == 'twitter.com':
                locs = [m.start() for m in re.finditer('/', o.path)]
                news_source += o.path[:locs[1]]
                twitter_feed_list.append(news_source)
            else:
                news_source_list.append(news_source)
        
        except:
            pass


    print 'Links Found: ', len(set(news_source_list))
    print 'Old Links: ', len(old_links)
    news_source_list  = list(set(news_source_list) - set(old_links)) 
    print 'New Links: ', len(news_source_list)
    twitter_feed_list = list(set(twitter_feed_list))

    news_rss_list = []
    for index, item in enumerate(news_source_list):
        print 'Feed: %d/%d' %(index, len(news_source_list))
        try:    
            rss = feedfinder.feeds(item)
            if rss is not None:
                rss.sort(key = lambda s: len(s))
                news_rss_list.append((item, rss[0]))
        except:
            pass

    return news_rss_list, twitter_feed_list

# get_feeds() ends


def main(load_flag = 0):

    url = 'http://techmeme.com/'
    save_file = 'feed_list.dat'

    # load data from the previous run
    if load_flag and os.path.isfile(save_file):
        data = pickle.load(open(save_file, 'rb' )) 
        rss_list     = data['rss_list']
        twitter_list = data['twitter_list']
    else:
        data = {}
        rss_list     = []
        twitter_list = []


    current_rss_size = len(rss_list)
    current_twitter_size = len(twitter_list)

    # get data from url now
    old_links = [item[0] for item in rss_list]
    rss, twitter = get_feeds(old_links, url)

    # add to the collection so far
    rss_list.extend(rss)
    twitter_list.extend(twitter)
    rss_list = list(set(rss_list))
    twitter_list = list(set(twitter_list))

    print rss_list
    print twitter_list
    print 'Added %d items to rss_list' %(len(rss_list) - current_rss_size)
    print 'Added %d items to twitter_list' %(len(twitter_list) - current_twitter_size)

    # save data to files
    data['rss_list']     = rss_list
    data['twitter_list'] = twitter_list
    pickle.dump(data, open(save_file, 'wb'))

# main() ends


if __name__ == '__main__':

    args = sys.argv[1:]

    if args:
        main(0)
    else:
        main(1)





