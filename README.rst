Scraper
=======

Minimalist Python HTML Scraper

Description
...........

This python package is intended to be

Installation
............

::

  python setup.py install


Usage
.....

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