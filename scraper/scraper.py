#coding: utf-8
import requests
from lxml import html
import datetime
import time
import pprint
import re
import sites
import logging
import hashlib
import threading
from Queue import Empty
from errors import RequestPageError
from datetime import date

class Scraper(threading.Thread):
    """ 
        Consumes scraper_jobs from a queue.
        Extracts relevant fields from each scraper_job URL.
        Publish results in an output queue
      
        DEPENDENCIES:
            * requests
            * lxml
            * datetime
            * re
    """

    def __init__(self, site_name, input_queue, output_queue, net_conf, name=None):
        """
        Instantiate new scraper using site name to load conf
        """
        threading.Thread.__init__(self, name=name)

        self.site = site_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.finished_crawling = False
        self.proxies = net_conf['proxies']
        self.user_agents = net_conf['user_agents']
        self.get_timeout = net_conf['get_timeout']

        #load site scraper conf from sites module:
        try:
            self.conf = getattr(sites, site_name)['scraper']
        except:
            errmsg = 'Couldn\'t load site scraper conf for %s' % site_name
            logging.error(errmsg)
            raise Exception(errmsg)

    def run(self):
        """
        Start consuming scraper_jobs from a queue and process them.
        Publish result documents in an output queue.
        """
        logging.info("Running scraper thread...")
        while (not self.finished_crawling or not self.input_queue.empty()):
            try:
                scraper_job = self.input_queue.get_nowait()
                url = scraper_job[0]
                result = {}
                try:
                    logging.info("scraping...")
                    result = self.scrape_page(url)
                except RequestPageError:
                    #log error and try with the next job
                    logging.error("Couldn't scrape url: %s" % url)
                    continue
                logging.debug("Scraped:")
                logging.debug([result])
                self.output_queue.put(result)
            except Empty:
                continue

        logging.info("scraper thread finished!")
        
    def scrape_page(self, url):
        response = requests.get(url, 
                                proxies = self.proxies,
                                headers = {'User-Agent': self.user_agents[0]},
                                timeout = self.get_timeout)
        if not response.ok:
            errmsg = "Error requesting url. Error code: %s. URL: %s" % (response.status_code, url)
            logging.error(errmsg)
            raise RequestPageError(errmsg)
        html_string = response.content
        page = html.fromstring(html_string)
        result = {}
        for field in self.conf['fields']:
            xpath = self.conf['fields'][field]['xpath']
            scraped = page.xpath("string(%s)" % xpath)
            scraped = scraped.strip()
            scraped = re.sub("[\n\t]","",scraped)
            if scraped in [None, '']:
                if 'default' in self.conf['fields'][field]:
                    result[field] = self.conf['fields'][field]['default']
            else:
                #encode field if character encoding is defined:
                if 'encoding' in self.conf['fields'][field]:
                    encoding = self.conf['fields'][field]['encoding']
                    if encoding is not None:
                        try:
                            scraped = scraped.encode(encoding)
                            #utf-8 is the encoding needed by mysolr
                            scraped = unicode(scraped, "utf-8")
                        except Exception as e:
                            logging.warn(e)
                            logging.warn("Error encoding %s field with provided encoding: %s" % (field, encoding))
                            logging.warn("  URL: %s" % url)
                            continue #dont include erroneous field
                #apply transformations (if defined)
                if 'transf' in self.conf['fields'][field]:
                    value = scraped
                    for func in self.conf['fields'][field]['transf']:
                        try:
                            value = func(value)
                        except Exception as e:
                            logging.error(e)
                            logging.error("Error applying %s transformation to %s field" % (func, field))
                            logging.error("  URL: %s" % url)
                            value = None
                            break #dont include erroneous field
                    if value is not None: result[field] = value
                    else: #we got None as a result of applying transformations
                        if 'default' in self.conf['fields'][field]:
                            result[field] = self.conf['fields'][field]['default']
                else:
                    result[field] = scraped

        result['indextime'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        result['site'] = self.site
        result['url'] = url
        result['rating'] = self.set_initial_value(result)
        result['id'] = hashlib.md5(url).hexdigest()
        
        return result
        
    def set_initial_value(self, result):
        atributes = getattr(sites, result['site'])['scraper']
        rating_factor = 30
        
        salary_rating = 0.0
        company_rating = 0.0
        date_rating = 0.0
        num_data = 0.0              
        
        for field in result:
            if field in atributes['fields']:
                num_data += 1                   
            if (field == 'min_salary') or (field == 'max_salary') or (field == 'salary'):
                salary_rating = 1.0
            if field == 'company':
                company_rating = 1.0
            if field == 'date':                 
                publication_date = datetime.date.fromtimestamp(time.mktime(time.strptime(result['date'], "%Y-%m-%dT%H:%M:%SZ")))                        
                today = datetime.date.today()
                delta = today - publication_date            
                date_rating = 1.0 / (delta.days +1) 
        data_rating = float(num_data)/len(atributes['fields'])      
        
        rating = (date_rating*40 + data_rating*30 + salary_rating*20 + company_rating*10)/100       
        
        return int(rating * rating_factor)	


if __name__ == '__main__':
  pp = pprint.PrettyPrinter(indent=4)
  net_conf = {  
                'proxies':
                {
                    'http': '188.40.53.67:3128',
                    'https': '188.40.53.67:3128'
                },
                'user_agents':
                [
                    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.X.Y.Z Safari/525.13.',
                    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; es-es) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
                ],
                'get_timeout': 60
             }
  
  #pp.pprint(scraper.scrape_page("http://www.example_info.net/cornella-de-llobregat/alumno-practicas-informatica/of-i44cd2faf064914b64f2eb13ac0cfc3"))  
  scraper = Scraper('example', None, None, net_conf, None)
  result = scraper.scrape_page('http://www.example_rand.es/content/findjobs/job-details/index.xml?currentPage=1&id=69556&__version=1')
  pp.pprint(result)
