"""Contains methods for loading articles from different sources"""

from xml.dom.minidom import parse, parseString
import motherlode

class NewsItem: # class for each news item

    identifier = 0 # static id for each news item
    
    def __init__(self, title, feed_title, link, author, content, updated_at):
        
        self.title = title
        self.feed_title = feed_title
        self.link = link
        self.author = author
        self.content = content
        self.updated_at = updated_at
        self.id = self.identifier
        self.identifier = self.identifier + 1
    
    
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

    xml_content = motherlode.getLatestDeltaDump() # get from redis

    dom = parseString(xml_content) # parse xml string

    items = get_items(dom)
            
    return items	
		
def load_xml_data(file_name): # loads the opml file

    dom = parse(file_name) # parse an XML file by name

    items = get_items(dom)
            
    return items	
    
