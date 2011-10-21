#!/usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import sys
import re
import time

from Queue import Queue
from scraper import Crawler
from scraper import Scraper
from scraper import Indexer

import yaml
import logging

def usage():
    print """
        execute_package.py [options]

options:

--help  Show help

-c      Config file (/etc/scraper/scraper.yml by default)

"""



def main(argv):

    #default values:
    conf_file_path = '/etc/scraper/scraper.yml'

    # Command line arguments
    try:
        optlist, args = getopt.getopt(argv, 'c:', ['help'])
        for opt, value in optlist:
            if opt == '--help':
                usage()
                sys.exit()
            elif opt == 'c':
                conf_file_path = value
    except getopt.GetoptError, err:
        print '\n' + str(err)
        usage()
        sys.exit(2)

    try:
        conf = yaml.safe_load(open(conf_file_path).read())
    except:
        print "error loading config file: %s" % conf_file_path
        sys.exit(2)

    #configure logging
    logging.basicConfig(filename=conf['log_file'], level=logging.INFO, format='%(asctime)s %(threadName)s %(message)s')

    logging.info('Running scrappers...')

    for site_name in conf['sites']:
        logging.info("****************************************************************")
        logging.info( "Go for %s!" % site_name)
        start_time = time.time()
        
        jobs_queue = Queue() #scraper jobs queue
        docs_queue = Queue() #docs to index queue

        crawler_thread = Crawler(site_name, jobs_queue, conf['net'], "Crawler")
        crawler_thread.start()

        scrapers = []
        for i in range(0, conf['scraper_threads_per_site']):
            scraper_thread = Scraper(site_name, jobs_queue, docs_queue, conf['net'], "Scraper-%s" % i)
            scrapers.append(scraper_thread)
            scraper_thread.start()

        indexers = []
        for i in range(0, conf['indexer_threads_per_site']):
            indexer_thread = Indexer(docs_queue, conf['solr_base_url'], conf['index_batch_size'], "Indexer-%s" % i)
            indexers.append(indexer_thread)
            indexer_thread.start()

        #wait until crawler ends
        crawler_thread.join()
        logging.info("Crawler thread finished.")

        #send a message to scrapers telling "crawler is no longer with us" and wait for each one to finish
        for scraper_thread in scrapers:
            scraper_thread.finished_crawling = True
            scraper_thread.join()

        logging.info( "All scraper threads finished.")

        #send a message to indexers telling "scrapers are no longer with us" and wait for each one to finish
        for indexer_thread in indexers:
            indexer_thread.finished_scraping = True
            indexer_thread.join()
        
        logging.info( "All indexer threads finished.")

        logging.info( "%s is DONE in %s seconds!" % (site_name, time.time() - start_time))
        logging.info("****************************************************************")

if __name__ == '__main__':
    main(sys.argv[1:])
