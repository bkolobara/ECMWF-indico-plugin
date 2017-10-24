from __future__ import unicode_literals

from setuptools import setup, find_packages


setup(
    name='ecmwf_indico_plugin',
    version='0.0.1',
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'indico>=2.0a1'
    ],
    entry_points={
        'indico.plugins': {'ecmwf = ecmwf_indico.plugin:ECMWFPlugin'}
    }
)