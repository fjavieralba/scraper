#coding: utf-8

import logging
from mysolr import Solr
import threading
from Queue import Empty
from errors import IndexError

class Indexer(threading.Thread):
    """ 
        Gets documents from an input queue and index them in SolR.
        If batch_size is defined, it will send documents in batches with maximum size of batch_size
        If batch_size is not defined it will send documents one by one
    """

    def __init__(self, docs_queue, base_url, batch_size = None, name=None):
        threading.Thread.__init__(self, name=name)

        self.batch_size = batch_size
        self.docs_queue = docs_queue
        self.finished_scraping = False

        self.mysolr = Solr(base_url)

        self.docs_to_index = []

    def run(self):
        """
        Start consuming docs from docs_queue and index them.
        """
        logging.info("running indexer thread...")

        while (not self.finished_scraping or not self.docs_queue.empty()):
            try:
                self.docs_to_index.append(self.docs_queue.get_nowait())
            except Empty:
                continue
            try:
                self.index_docs()
            except IndexError as e:
                logging.error("Error indexing documents. source: %s" % e)
                continue

        logging.info("indexer main loop ended. lets index remaining docs...")
        self.index_remaining_docs()

        logging.info("indexer thread finished!")

    def index_docs(self):
        """
            Check the current list of documents waiting to be indexed and index them.
            If batch_size is defined, don't index them until we have enough
        """
        if self.batch_size: #submit docs in batches
            while len(self.docs_to_index) >= self.batch_size:
                batch = self.docs_to_index[0:self.batch_size]
                self.docs_to_index = self.docs_to_index[self.batch_size:]
                logging.info("indexing batch with size %s" % len(batch))
                self.index(batch)
        else: #submit all docs in docs_to_index:
            logging.info("indexing %s documents..." % len(self.docs_to_index))
            self.index(self.docs_to_index)

            #clean docs_to_index list
            self.docs_to_index = []

    def index_remaining_docs(self):
        logging.info("indexing %s remaining documents..." % len(self.docs_to_index))
        self.index(self.docs_to_index)
        
    def index(self, docs):
        try:
            self.mysolr.update(docs, 'json')
            self.mysolr.commit()
        except Exception as e:
            logging.error(e)
            logging.error(docs)
            raise IndexError(e)

if __name__ == '__main__':
    doc = {'contract': u'con posible incorporaci\xf3n a plantilla',
    'date': '2011-07-19T00:00:00Z',
    'description': u'La delegaci\xf3n ubicada en Gij\xf3n de una importante multinacional dedicada al sector de la soldadura precisa aux. administrativo/a con manejo de contapl\xfas y facturaplus as\xed como nivel alto de ingl\xe9s.\rIncorporaci\xf3n inmediata.\rEstabilidad laboral',
    'hours': 'Completa',
    'id': '083052804b0d67982615cf8eff5c52d5',
    'indextime': '2011-07-21T08:39:09Z',
    'max_salary': 17000.0,
    'min_salary': 16000.0,
    'municipality': u'Gij\xf3n, 33210',
    'rating': 0,
    'reference': 'R79966',
    'site': 'randstad',
    'studies': u'05 | Diplomado\ren\rCiencias Empresariales',
    'title': 'ADMINISTRATIVO/A INGLES (m/v)',
    'url': 'http://www.example_rand.es/content/findjobs/job-details/index.xml?currentPage=1&id=79966&__version=1',
    'vacancies': '1'}

    indexer = Indexer(None, 'http://my_solr:8080/solr')
    indexer.index([doc])
        