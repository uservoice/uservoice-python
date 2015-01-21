import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='uservoice',
      version='0.0.20',
      description='UserVoice Python library',
      url = 'http://pypi.python.org/pypi/uservoice/',
      long_description=re.sub(r'```[^\s]*', '', open('README.md').read()),
      author='Raimo Tuisku',
      author_email='dev@uservoice.com',
      packages=['uservoice'],
      install_requires=[
          'simplejson',
          'pycrypto',
          'pytz',
          'PyYAML',
          'requests',
          'future',
          'requests-oauthlib'],
      test_suite='test',
)
