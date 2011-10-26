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
...     'trending-repos' : {'xpath' : '//ol[@class="ranked-repositories"]/li/h3'}
... }
>>> 
>>> scraper.scrapes(content, conf)

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