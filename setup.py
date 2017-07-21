#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pip

from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

parsed_requirements = parse_requirements(
    'requirements/prod.txt',
    session=pip.download.PipSession()
)

requirements = [str(ir.req) for ir in parsed_requirements]


setup(
    name='rocket_snake',
    version='0.1.2',
    description="Rocket Snake is a client library to access the rocketleaguestats.com API in python with async code.",
    long_description=readme + '\n\n' + history,
    author="Hugo Berg",
    author_email='hb11002@icloud.com',
    url='https://github.com/drummersbrother/rocket_snake',
    packages=[
        'rocket_snake',
    ],
    package_dir={'rocket_snake':
                 'rocket_snake'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache",
    zip_safe=False,
    keywords='rocket_snake',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
