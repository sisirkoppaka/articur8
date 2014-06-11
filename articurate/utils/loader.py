"""Contains methods for loading articles from different sources"""

from xml.dom.minidom import parse, parseString
import urllib2
from urlparse import urlparse,urlunparse
#from ..pymotherlode import motherlode
#from .. import pymotherlode
from articurate.pymotherlode.api import *

#from urlparse import urlparse, urlunparse
from articurate.utils.class_definitions import NewsItem     
 
    
def clean_link(link):
    #Clean link
    #Starting with eliminating redirects
    l = urllib2.urlopen(link)
    link = l.geturl()
    #And dropping params, queries and fragments
    link_parsed = urlparse(link)
    core_link_parsed = (link_parsed.scheme,link_parsed.netloc,link_parsed.path,'','','')
    link = urlunparse(core_link_parsed)
    return link

def clean_link_only_redirects(link):
    #Clean link
    #Starting with eliminating redirects
    #l = urllib2.urlopen(link)
    #link = l.geturl()
    #And dropping params, queries and fragments
    link_parsed = urlparse(link)
    core_link_parsed = (link_parsed.scheme,link_parsed.netloc,link_parsed.path,'','','')
    link = urlunparse(core_link_parsed)
    return link


def get_items(dom):
	
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
		

def deduplicate(articles):

    selected_articles = []

    for i in range(0, len(articles)):
        ignore = False
        for j in range(0, len(articles)):
            if i != j and articles[i].title == articles[j].title and articles[i].feed_title == articles[j].feed_title and articles[i].updated_at <= articles[j].updated_at:
                ignore = True
                break
        if not ignore:
            selected_articles.append(articles[i])

    return selected_articles

		
def get_all_dumps():

    xml_content_list = getAllDumps() 

    items = get_items_from_xml_list(xml_content_list)

    return items


def get_latest_dump():

    xml_content = getLatestDeltaDump() # get from redis
    
    items = get_items_from_xml_list([xml_content])

    return items	
	

def collect_last_dumps():

    xml_content_list = getAllCacheDumps() 
    
    items = get_items_from_xml_list(xml_content_list)

    return items


def get_items_from_xml_list(xml_content_list):

    items = []

    for xml_content in xml_content_list:
        try:
            dom = parseString(xml_content)
            items.extend(get_items(dom))
        except:
            pass

    print "\nFinished loading ", len(items), " articles\n"

    items = deduplicate(items)

    print "\nAfter deduplication ", len(items), " articles\n"

    return items


def load_xml_data(file_name): # loads the opml file

    dom = parse(file_name) # parse an XML file by name

    items = get_items(dom)
            
    return items	
    
