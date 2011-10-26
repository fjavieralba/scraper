scraper
=======

Configurable Python Web Scraper

Usage
.....

Scrape using xpath:
-------------------

>>> import scraper
>>> import requests
>>> 
>>> content = requests.get('https://github.com/explore').content
>>> 
>>> conf = {
...     'trending-repos' : {'xpath' : //ol/li/h3/a[2]/@href}
... }
>>> 
>>> scraper.scrapes(content, conf)
{'trending-repos': ['/jamescryer/grumble.js', '/dominictarr/JSON.sh', '/JamieLottering/DropKick', '/harvesthq/chosen', '/velvia/ScalaStorm']}

Scrape using regexp:
--------------------

>>> import scraper
>>> import requests
>>> 
>>> content = requests.get('http://wiki.nomasnumeros900.com/Air_Liquide').content
>>> 
>>> conf = {
...     'numbers': {'regexp': '91[\s\d]+'}
... }
>>> 
>>>scraper.scrapes(content, conf)
>>>
>>> scraper.scrapes(content, conf)
{'numbers': ['915 029 300', '915 029 560 ', '915 029 330 \n', '91 ']}