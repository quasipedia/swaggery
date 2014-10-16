#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    # Authoring
    name='swaggery',
    version='1.0.0a1',
    description='A Python3 framework to create self-documenting swagger APIs',
    long_description=long_description,
    url='https://github.com/quasipedia/swaggery',
    author='Mac Ryan',
    author_email='quasipedia@gmail.com',
    license='AGPLv3+',
    keywords='swagger API documentation asyncronous framework uWSGI WSGI',

    # Classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'License :: OSI Approved :: '
            'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Documentation',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # Dependencies
    install_requires=[
        'uWSGI==2.0.7',
        'Werkzeug==0.9.6',
        'jsonschema==2.4.0',
        'docopt==0.6.2',
    ],
    extras_require={
        'dev': [
            'wheel==0.24.0',
            'pip==1.5.6',
        ],
        'test': [
            'coverage==3.7.1',
            'nose==1.3.4',
            'rednose==0.4.1',
        ],
    },

    # Content
    py_modules=['wsgi_application'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={
        'swaggery': ['static/*'],
    },
    data_files=[('examples', ['examples/*'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
