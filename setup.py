# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='tummy-time',
    version='0.0.1',
    description='Get estimates for food delivery time',
    license='Apache Software License',
    long_description=readme,
    author='Haim Daniel',
    author_email='haimdaniel@gmail.com',
    url='https://github.com/haim0n/tummy_time',
    packages=find_packages(exclude=('tests')),
    test_suite='tummy_time.test.test_tummy_time',
    install_requires=['google-api-python-client',
                      'oauth2client>=2.0.1',
                      'httplib2',
                      'six',
                      'tinydb',
                      ],
    tests_require=['tox'],
    extras_require={
        'testing': ['pytest'],
    }
)
