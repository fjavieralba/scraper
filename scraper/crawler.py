#coding: utf-8
import requests
from lxml import html
import time
import logging
import sites
import threading
import yaml
from Queue import Queue
from errors import RequestPageError

class Crawler(threading.Thread):
    """ 
        Navigates a WebPage and extracts links. Publish extracted links into a queue 
		
        DEPENDENCIES:
                * requests
                * lxml

        TODO: 	* User Agent management
                * Random Time waits
                * study if it's better to use lxml.html.html5parser
                * improve "finished" test
    """

    def __init__(self, site_name, results_queue, net_conf, name=None):
        """
        Instantiate new crawler thread using site name to load conf
        """
        threading.Thread.__init__(self, name=name)

        #load site crawler conf from sites module:
        try:
            self.conf = getattr(sites, site_name)['crawler']
        except:
            errmsg = 'Couldn\'t load site crawler conf for %s' % site_name
            logging.error(errmsg)
            raise Exception(errmsg)

        #set crawler attributes:
        self.site_name = site_name
        self.proxies = net_conf['proxies']
        self.user_agents = net_conf['user_agents']
        self.get_timeout = net_conf['get_timeout']

        self.results_queue = results_queue


    def run(self):
        """
        Run the crawler against a site, according to his conf. Publish scraper_jobs into a queue.
        """
        logging.info("running crawler thread...")
        #request, parse and process start page:
        logging.info("requesting start_url: "+self.conf['start_url'])
        response = requests.get(self.conf['start_url'], 
                                proxies = self.proxies, 
                                headers = {'User-Agent': self.user_agents[0]},
                                timeout = self.get_timeout)
        if not response.ok:
            errmsg = "Could not load start page.\n  URL: %s\n  Error code: %s" % (self.conf['start_url'], response.status_code)
            logging.error(errmsg)
            raise RequestPageError (errmsg)
        html_string = response.content
        tree = html.fromstring(html_string)
        logging.info("processing first page...")
        self.process_page(tree, self.results_queue)
        logging.info("ok")
        #process the rest of pages:
        while not self.finished(tree):
            tree = self.navigate(tree)            
            self.process_page(tree, self.results_queue)
            time.sleep(self.conf['request_wait'])

    def process_page(self, tree, results_queue):
        """
        Process a page to extract relevant links
        """		
        #retrieve element list
        element_list = []
        #for xpath_expr in self.conf['elements_xpaths']:
            #for element in tree.xpath(xpath_expr):
                #element_list.append(element)
        for element in tree.xpath(self.conf['elements_xpath']):
            element_list.append(element)
        if len(element_list) == 0: logging.warn("No links could be extracted")
        for element in element_list:
            if (self.conf['elements_transf'] is not None):
                try:
                    element = self.conf['elements_transf'](element)
                except:
                    logging.error("Error applying elements transformation to element: %s" % element)
                    break #dont include erroneous element
                    
            queue_item = (element, self.site_name)
            results_queue.put(queue_item, True)
		
    def navigate(self, tree):
        """
        Try no navigate to next page, updating the tree
        """
        #extract next_page link:
        next_page_url = tree.xpath(self.conf['nextpage_url_xpath'])
        #apply transformation if defined:
        if (self.conf['nextpage_url_transf'] is not None):
            try:
                next_page_url = self.conf['nextpage_url_transf'](next_page_url)
            except:
                logging.error("Error applying next_page_url transformation to url: %s" % next_page_url)
        #request next page:
        logging.info("Requesting: "+next_page_url)               
        response = requests.get(next_page_url,
                                proxies = self.proxies,
                                headers = {'User-Agent': self.user_agents[0]},
                                timeout = self.get_timeout)
        if not response.ok:
            logging.error("Error requesting page.\n  URL: %s\n  Error code: %s" % (next_page_url, response.status_code))
            logging.error("Retrying...")
            #return old tree to retry again and again:
            return tree
        else:
            #return updated tree
            html_string = response.content
            return html.fromstring(html_string)

    def finished(self, tree):
        """ This function determines if the pagination cycle has finished
            This happens when there are no hits for next_page_xpath expression
        """
        if not (len(tree.xpath(self.conf['nextpage_url_xpath'])) > 0): return True
        else: return False
if __name__ == '__main__':
	#pp = pprint.PrettyPrinter(indent=4)
	conf_file_path = '/etc/scraper/scraper.yml'
	conf = yaml.safe_load(open(conf_file_path).read())
	jobs_queue = Queue() #scraper jobs queue
	docs_queue = Queue() #docs to index queue	
	crawler_thread = Crawler('example', jobs_queue, conf['net'], "Crawler")	
	crawler_thread.start()
  
  
  