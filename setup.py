from __future__ import unicode_literals

from setuptools import setup, find_packages

# Read README.md file into description
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='ecmwf_plugin',
    version='0.0.4',
    author='Bernard Kolobara',
    description='This Indico plugin provides a set of features specific to the ECMWF',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'indico>=2.2'
    ],
    entry_points={
        'indico.plugins': {'ecmwf = ecmwf.plugin:ECMWFPlugin'}
    },
    classifiers=[
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.7',
    ],
)