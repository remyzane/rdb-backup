#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


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
    packages=find_packages(),
    package_data={'rdb_backup': ['*.yml'] },
    test_suite="tests",
    install_requires=[
        # 'pytest',
        'click',
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'rdb-backup=rdb_backup.command:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4'
    ]
)
