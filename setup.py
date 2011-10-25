# -*- coding: utf-8 -*-
from distutils.core import setup

import scraper

setup(name = 'scraper',
      version = '1.0',
      description = 'Configurable Python Web Scraper',
      author = scraper.__author__,
      author_email = scraper.__email__,
      url = 'https://github.com/fjavieralba/scraper',
      data_files = [('/etc/scraper', ['conf/scraper.yml'])],
      packages = ['scraper', 'scraper.sites'],
      scripts = ['scripts/run_scraper.py']
      )
