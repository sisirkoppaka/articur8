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

    print "Finished loading ", len(items), " articles\n"

    return items
		
		
def get_latest_dump():

    xml_content = getLatestDeltaDump() # get from redis

    dom = parseString(xml_content) # parse xml string

    items = get_items(dom)
            
    return items	
	

def collect_last_dumps():

    xml_content_list = getAllCacheDumps() 

    items = []

    for xml_content in xml_content_list:
        dom = parseString(xml_content)
        items.extend(get_items(dom))

    return items


def load_xml_data(file_name): # loads the opml file

    dom = parse(file_name) # parse an XML file by name

    items = get_items(dom)
            
    return items	
    
