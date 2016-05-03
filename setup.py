#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup


def read(*paths):
    """ read files """
    with open(os.path.join(*paths), 'r') as filename:
        return filename.read()


def get_package_data(package):
    """ Return all files under the root package, that are not in a package themselves."""

    walk = [(dir_path.replace(package + os.sep, '', 1), file_names)
            for dir_path, dir_names, file_names in os.walk(package)
            if not os.path.exists(os.path.join(dir_path, '__init__.py'))]
    file_paths = []
    for base, file_names in walk:
        file_paths.extend([os.path.join(base, file_name)
                          for file_name in file_names])
    return {package: file_paths}

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
    package_data=get_package_data('rdb_backup'),
    test_suite="tests",
    install_requires=[
        'pytest',
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
