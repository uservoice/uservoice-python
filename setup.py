import os
import sys
import re
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='uservoice',
      version='0.0.24',
      description='UserVoice Python library',
      url = 'http://pypi.python.org/pypi/uservoice/',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      author='UserVoice Inc.',
      author_email='dev@uservoice.com',
      packages=setuptools.find_packages(),
      install_requires=[
          'pycryptodome',
          'pytz',
          'PyYAML',
          'requests',
          'future',
          'requests-oauthlib'],
      test_suite='test',
)
