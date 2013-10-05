# by SK and AM

import nltk
import re
import urllib2
import opml
import feedparser
import boto
import simplejson
from time import mktime
from datetime import datetime, date, time, timedelta
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree
import logging
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import requests
from urlparse import urlparse,urlunparse
from readability.readability import Document

AWS_ACCESS_KEY_ID = "NOTHING"
AWS_SECRET_ACCESS_KEY = "NOTHING"
SERVER_URL = "http://localhost:9999/"


class RSSObj: # object to store the rss feeds
    def __init__(self, title, xmlUrl, htmlUrl = None):
        
        self.title = title
        self.xmlUrl = xmlUrl
        self.htmlUrl = "" if htmlUrl == None else htmlUrl
        

class OutlineObj: # object which we store for each entry
    def __init__(self, title = None, link = None, author = None):

        self.title = "None" if title == None else title
        self.link = "None" if link == None else link
        self.author = "None" if author == None else author

        if link == None:
            cleaned = "None"
        else: # get the content by parsing the link
            try:
                link_connect = urllib2.urlopen(link)
                self.link = clean_link(link_connect)
                html = link_connect.read()
                try:
                    raw = nltk.clean_html(Document(html).summary())
                except:
                    raw = nltk.clean_html(html)
                cleaned = " ".join(re.split(r'[\n\r\t ]+', raw))
                #The following unicode line raises exceptions sometimes. 
                #The lack of a fix for now is causing some articles to not have any content
                #cleaned = unicode(cleaned, "utf-8") # TO DO : fix this
                cleaned.replace("&", "")
            except:
                cleaned = "None"
        
        #print "Length of cleaned HTML",len(cleaned)
        #print cleaned    
        self.content = cleaned
        self.updatedAt = ""

def putCloud(type, name):
    c = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    b = c.create_bucket('alpha.socialgrep.com')
    k = Key(b)
    k.key=type+'/'+name
    k.set_contents_from_filename(name)
    k.key=type+'/'+"latest.opml"
    k.set_contents_from_filename(name)
    return

#TODO Avoid double urlopen of link here and in Outline later
def clean_link(link_connect):
    #Clean link
    #Starting with eliminating redirects
    link = link_connect.geturl()
    #And dropping params, queries and fragments
    link_parsed = urlparse(link)
    core_link_parsed = (link_parsed.scheme,link_parsed.netloc,link_parsed.path,'','','')
    link = urlunparse(core_link_parsed)
    return link

def clean_link_only_redirects(link):
    #Clean link
    #Starting with eliminating redirects
    l = urllib2.urlopen(link)
    link = l.geturl()
    return link

def storeDeltaDump(timestamp,deltadump):
    payload = {'timestamp':timestamp,'deltadump':deltadump}
    r = requests.post(SERVER_URL+"dumps/delta/",data=payload)

def prettify(element):
    rough_string = ElementTree.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def genStringID():
    """docstring for genStringID"""
    return (datetime.utcnow()).strftime('%Y%m%d%H%M')

def getRSSSources():
    """Gets all the RSS sources we want to mine from
    and returns a list of rss objects"""

    rss_sources = []

    # add required sources

    # add techmeme sources
    techmeme_sources = opml.parse('http://www.techmeme.com/lb.opml')
    for item in techmeme_sources:
        try:
            if hasattr(item, 'htmlUrl'):
                rss_sources.append(RSSObj(item.text, item.xmlUrl, item.htmlUrl))
            else:
                rss_sources.append(RSSObj(item.text, item.xmlUrl))
        except:
            pass

    return rss_sources

def getEntryContent(entry): # gets whatever field information is present in entry

    # get whatever fields are available
    title = entry.title if hasattr(entry, 'title') else "None"
    link = entry.link if hasattr(entry, 'link') else "None"

    content = ""
    index = 0
    if hasattr(entry, 'content'):
        while True:
            try:
                content = content + entry.content[index].value
                index = index + 1
            except:
                break
    else:
        content = "None"
    
    author = entry.author if hasattr(entry, 'author') else "None"

    #print "title = ", title
    #print "link = ", link
    #print "content = ", content
    #print "author = ", author
    #dummy = raw_input()

    outline = OutlineObj(title, link, author) # create the outline object

    updatedAt = entry.updated_parsed if hasattr(entry, 'updated_parsed') else "None"
    outline.updatedAt = updatedAt
    
    return outline

def genSnapshot(endTime):
    """dumps articles found in [currentTime-endTime:currentTime] minutes"""

    stringID = genStringID() # generates a unique ID based on time
    generated_on = datetime.utcnow()

    # set up python logger  
    logger = logging.getLogger("["+stringID+"]")
    logger.setLevel(logging.INFO)

    # get RSS sources
    rss_sources = getRSSSources()
    logger.info("Num RSS sources "+str(len(rss_sources)))
    print "Num RSS sources = ", len(rss_sources)

    # create an xml tree
    root = Element('opml')
    root.set('version','1.0')
    root.append(Comment('Generated by FeedDigger'))
    
    head = SubElement(root, 'head')

    title = SubElement(head, 'title')
    title.text = 'grep last '+str(endTime)+' minutes '+stringID
    
    dc = SubElement(head, 'dateCreated')
    dc.text = str(generated_on)

    dm = SubElement(head,'dateModified')
    dm.text = str(generated_on)
    
    body = SubElement(root, 'body')

    logger.info("Starting "+str(generated_on))

    num_added = 0

    # get entries from each of the rss sources
    for source in rss_sources:
        try:
            d = feedparser.parse(source.xmlUrl) # parse from rss source
            try:               
                logger.info("Parsed "+d.feed.title)                  
                for entry in d.entries:
                    if (datetime(*entry.updated_parsed[:6]) > (generated_on-timedelta(minutes = endTime))) and (datetime(*entry.updated_parsed[:6]) < (generated_on)):
                        # entry lies in required range
                        logger.info("Found "+entry.title+" at "+d.feed.title)

                        num_added = num_added + 1
                        print num_added

                        outline = getEntryContent(entry)

                        # create xml entry
                        item = SubElement(body, 'item')

                        # create xml title
                        title = SubElement(item, 'title')
                        title.text = outline.title

                        # create xml feed title
                        feedTitle = SubElement(item, 'feed_title')
                        feedTitle.text = d.feed.title

                        # create xml link
                        link = SubElement(item, 'link')
                        link.text = outline.link

                        # create xml author
                        author = SubElement(item, 'author')
                        author.text = outline.author

                        # create xml content
                        content = SubElement(item, 'content')
                        content.text = outline.content

                        # create xml timestamp
                        UpdatedAt = SubElement(item, 'updated_at')
                        UpdatedAt.text = str(datetime.fromtimestamp(mktime(outline.updatedAt)))
                        
                        

            except TypeError:
                    pass   
        except UnicodeEncodeError:
                pass
        except AttributeError:
                pass

    # output data to file
    #fout = open('../feeddumps/'+stringID+".opml",'w')
    #fout.write((prettify(root)).encode('utf-8'))
    #fout.close()
    storeDeltaDump(stringID,(prettify(root)).encode('utf-8'))

    #putCloud("river",stringID+".opml")
    #os.remove(stringID+".opml")

    logger.info("Ended "+str(datetime.utcnow()))

if __name__ == "__main__":
    LOG_FILENAME_INFO = 'feeddigger_info.log'
    logging.basicConfig(filename=LOG_FILENAME_INFO, level=logging.INFO)

    endTime = 500# below gets stuff in time range of (currenTime) minutes to (currentTime - endTime) minutes

    genSnapshot(endTime)