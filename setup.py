#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup


def read(*paths):
    """ read files """
    with open(os.path.join(*paths), 'r') as filename:
        return filename.read()

setup(
    name="rdb-backup",
    version="0.0.1",
    description="backup and restore relational database e.g. postgresql, mysql",
    long_description=(read('README.md')),
    license='MIT',
    author="Remy Zane",
    author_email="remyzane@icloud.com",
    url="https://github.com/remyzane/rdb-backup",
    packages=['rdb_backup'],
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'rdb-backup=rdb_backup:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4'
    ]
)
