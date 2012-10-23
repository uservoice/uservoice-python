import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='uservoice',
      version='v0.0.2',
      description='UserVoice Python library',
      long_description=open('README.md').read(),
      author='Raimo Tuisku',
      author_email='dev@uservoice.com',
      packages=['uservoice'],
      install_requires=[
          'simplejson',
          'pycrypto',
          'pytz',
          'PyYAML',
          'requests-oauth'],
      test_suite='test',
)