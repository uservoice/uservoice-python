import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='uservoice',
      version='v0.0.1',
      description='UserVoice Python library',
      author='Raimo Tuisku',
      author_email='dev@uservoice.com',
      url='http://uservoicetripe.com/',
      packages=['uservoice'],
      install_requires=[
          'simplejson',
          'pycrypto',
          'pytz',
          'PyYAML',
          'tweepy'],
      test_suite='test',
)