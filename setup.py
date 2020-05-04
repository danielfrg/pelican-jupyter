#!/usr/bin/env python3

"""Setup script for ipynb."""

from setuptools import find_packages
from setuptools import setup

setup(
    name="ipynb",
    version="0.1",
    description="Pelican plugin for blogging with Jupyter/IPython Notebooks",
    author="Daniel Rodriguez",
    url="https://github.com/danielfrg/pelican-ipynb",
    packages=find_packages(),
)
