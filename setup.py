#!/usr/bin/env python

from setuptools import setup, find_packages

__author__ = "Jordan Ovrè <ghecko78@gmail.com>"

description = 'Hydrabus framework module to recover SPI chip ID'
name = 'hbfmodules.spi.chip_id'
setup(
    name=name,
    version='0.0.2',
    packages=find_packages(),
    license='GPLv3',
    description=description,
    author=__author__,
    url='https://github.com/hydrabus-framework/' + name,
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha'
    ],
    keywords=['hydrabus', 'framework', 'hardware', 'security', 'spi', 'chip_id']
)
