#coding: utf-8

""" 
    Scrape an HTML file to extract relevant parts   
  
    The scraping configuration is a parameter to each of its public methods.

    DEPENDENCIES:
        * lxml
        * re
"""

from lxml import html
import re

def scrape(fd, conf):
    return scrapes(fd.read(), conf)
        
def scrapes(html_string, conf):
    html_tree = html.fromstring(html_string)
    return process(html_tree, html_string, conf)

def process(html_tree, html_string, conf):
    result = {}
    for field in conf:
        #extract field content with xpath or regexp:
        scraped = None
        if 'xpath' in conf[field]:
            xpath = conf[field]['xpath']
            scraped = html_tree.xpath(xpath)
            if isinstance(scraped, list): #element list
                try:
                    scraped = map(lambda x : x.text, scraped)
                except:
                    pass
        elif 'regexp' in conf[field]:
            regexp = conf[field]['regexp']
            scraped = re.findall(regexp, html_string)
        
        if scraped is not None:
            #encode field if character encoding is defined:
            if 'encoding' in conf[field]:
                encoding = conf[field]['encoding']
                if encoding is not None:
                    if isinstance(scraped, list): #list value
                        try:
                            scraped = map(lambda x : x.decode(encoding), scraped)
                        except Exception as e:
                            print "Error decoding %s field: %s" % (field, e)
                    else: #single value
                        try:
                            scraped = scraped.decode(encoding)
                        except Exception as e:
                            print "Error decoding %s field: %s" % (field, e)
    
            #apply transformations (if defined)
            if 'transf' in conf[field]:
                #apply transformations in chain:
                for func in conf[field]['transf']:
                    if isinstance(scraped, list): #list value
                        try:
                            scraped = map(func, scraped)
                        except Exception as e:
                            print "Error applying function %s to element list: %s" % (func, e)
                            scraped = None
                            break #dont include erroneous field
                    else: #single value:
                        try:
                            scraped = func(scraped)
                        except Exception as e:
                            print "Error applying func %s to field value %s" % (func, scraped)
                            scraped = None
                            break #dont include erroneous field
                if scraped is None: #some error occurred as a result of applying transformations
                    if 'default' in conf[field]:
                        scraped = conf[field]['default']
        result[field] = scraped

    return result	
    
