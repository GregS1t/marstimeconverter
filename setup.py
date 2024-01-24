#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages

#import marsconverter
 

setup(
 
    
    name='marsconverter',
 
    # la version du code
    version='0.1',
 
    packages=find_packages(),
 
    author="Planetology and Space Sciences",
 
    author_email="sainton@ipgp.fr",
 
    description="Convert UTC Date Time to Mars Time",
 
    long_description=open('README.md').read(),
 
    include_package_data=True,
 
    url='https://pss-gitlab.math.univ-paris-diderot.fr/sainton/aspic',
 

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Production/Stable",
        "License :: MIT Licence",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],

)
