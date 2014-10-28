from bs4 import BeautifulSoup
from urlparse import urlparse
import requests
import re
import feedfinder 
import time
import pickle
import os.path
import sys
from time import gmtime, strftime
import feedparser
import signal

def handler(signum, frame):
    
    print "Forever is over!"
    raise Exception("end of time")

# handler() ends


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
            
            # put a timeout as feedfinder can stall indefinitely
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(10)

            rss = feedfinder.feeds(item)

            # cancel timeout if feedfinder returned
            signal.alarm(0)

            if rss is not None and len(rss) > 0:
                rss.sort(key = lambda s: len(s))
                news_rss_list.append((item, rss[0]))

        except Exception, exc:
            print exc
            pass

    return news_rss_list, twitter_feed_list

# get_feeds() ends


def scrape_sources(keyword, url):

    save_file = 'feed_lists/%s_feed_list.dat' % keyword

    # load data from the previous run
    if os.path.isfile(save_file):
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
    old_links    = [item[0] for item in rss_list]
    rss, twitter = get_feeds(old_links, url)

    # add to the collection so far
    new_rss_list = list(set(rss) - set(rss_list))
    rss_list.extend(rss)
    twitter_list.extend(twitter)
    rss_list     = list(set(rss_list))
    twitter_list = list(set(twitter_list))

    # print rss_list
    # print twitter_list
    print '%s::Added %d items to rss_list' %(keyword, len(rss_list) - current_rss_size)
    print '%s::Added %d items to twitter_list' %(keyword, len(twitter_list) - current_twitter_size)

    # save data to files
    data['rss_list']     = rss_list
    data['twitter_list'] = twitter_list
    pickle.dump(data, open(save_file, 'wb'))

    create_opml(keyword, new_rss_list)


# scrape_sources() ends


def create_opml(keyword, rss_list):

    save_file = 'feed_lists/%s_feed_list.opml' % keyword

    # read in existing opml file if any
    lines = []
    if os.path.isfile(save_file):
        for line in open(save_file, 'r'):
            if 'outline' in line:
                lines.append(line)
    
    # overwrite or create opml file
    fout = open(save_file, 'w')
    fout.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n<opml version="1.1">\n<head>\n\t<title>%s sources</title>\n\t<dateModified>%s</dateModified>\n</head>\n<body>\n' %(keyword, strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    # write stuff from previous opml file
    for line in lines:
        fout.write(line)

    for count, item in enumerate(rss_list):
        try:
            print '%d/%d' %(count, len(rss_list))
            
            # put a timeout as feedparser can stall indefinitely
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(10)

            feed = feedparser.parse(item[1])

            # cancel timeout if feedfinder returned
            signal.alarm(0)

            title = feed['channel']['title']
            title = title.replace('"', "'")
            title = title.replace('&', '&amp;')

            fout.write('\t<outline text="%s" type="rss" htmlUrl="%s" xmlUrl="%s"/>\n' %(title, item[0], item[1]))
        except:
            pass

    fout.write('</body>\n</opml>')
    fout.close()


# update_opml() ends

if __name__ == '__main__':

    streams = {}
    streams['tech']  = 'http://techmeme.com/';
    streams['media'] = 'http://www.mediagazer.com/';

    for key, url in streams.iteritems():
        scrape_sources(key, url)





