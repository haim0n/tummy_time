# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tummy-time',
    version='0.0.1',
    description='Get estimates for food delivery time',
    long_description=readme,
    author='Haim Daniel',
    author_email='haimdaniel@gmail.com',
    url='https://github.com/haim0n/tummy_time',
    license=license,
    packages=find_packages(exclude=('tests'))
)

