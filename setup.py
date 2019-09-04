import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='uservoice',
      version='0.0.24',
      description='UserVoice Python library',
      url = 'http://pypi.python.org/pypi/uservoice/',
      long_description=re.sub(r'```[^\s]*', '', open('README.md').read()),
      long_description_content_type="text/markdown",
      license='MIT',
      author='UserVoice Inc.',
      author_email='dev@uservoice.com',
      packages=['uservoice'],
      install_requires=[
          'pycryptodome',
          'pytz',
          'PyYAML',
          'requests',
          'future',
          'requests-oauthlib'],
      test_suite='test',
)
