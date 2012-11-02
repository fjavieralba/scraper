
Scraper
#######


Minimalist Python DOM Scraper

Description
===========

This module is an easy to use HTML/XML scraper. It supports both XPath and Regular 
Expression retrieval.

Once you have a file you want to extract information from, you can extract
multiple pieces of information with a simple function call.

You should obtain the files you want to scrape by your own ways.


Installation
============

::

  pip install scraper


Usage
=====

Scrape using xpath:
-------------------

::

    import scraper
    import requests
     
    content = requests.get('https://github.com/explore').content
     
    conf = {'trending-repos' : {'xpath' : '//ol/li/h3/a[2]/@href'}}

    scraper.scrapes(content, conf)

    >>> {'trending-repos': ['/jamescryer/grumble.js', '/dominictarr/JSON.sh', '/JamieLottering/DropKick', '/harvesthq/chosen', '/velvia/ScalaStorm']}

Scrape using regexp:
--------------------

::

    import scraper
    import requests

    content = requests.get('http://wiki.nomasnumeros900.com/Air_Liquide').content
     
    conf = {
            'numbers': 
                {'regexp': '91[\s\d]+', 
                 'transf': [lambda x: x.strip()], 
                 'encoding': 'utf-8'}
            }

    scraper.scrapes(content, conf)

    >>> {'numbers': [u'915 029 300', u'915 029 560', u'915 029 330', u'91']}
