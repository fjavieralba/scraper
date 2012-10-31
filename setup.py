# -*- coding: utf-8 -*-
from distutils.core import setup

setup(  name = 'scraper',
        version = '0.1.0',
        author='F. Javier Alba',
        author_email='me@fjavieralba.com',
        packages = ['scraper'],
        url='http://pypi.python.org/pypi/scraper/',
        license='LICENSE.txt',
        description = 'Configurable Python Web Scraper',
        long_description=open('README.rst').read(),
        install_requires=[
            "lxml >= 3.0.1",
        ],
    )