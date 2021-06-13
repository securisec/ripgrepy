from setuptools import setup, find_packages
from os import path

__version__ = '1.1.0'
__author__ = 'Hapsida @securisec'

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    long_description=long_description,
    long_description_content_type='text/markdown',
    name="ripgrepy",
    version=__version__,
    author=__author__,
    url='https://github.com/securisec/ripgrepy',
    project_urls={
        'Documentation': 'https://ripgrepy.readthedocs.io/',
        'CI': 'https://travis-ci.com/github/securisec/ripgrepy',
    },
    packages=find_packages(),
    install_requires = [
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7"
    ]
)
