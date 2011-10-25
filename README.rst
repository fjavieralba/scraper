scraper
=======

Configurable Python Web Scraper

Usage
.....

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