[![Build Status](https://travis-ci.com/securisec/ripgrepy.svg?branch=master)](https://travis-ci.com/securisec/ripgrepy)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](http://ripgrepy.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/ripgrepy.svg?logo=python&color=blue)](https://pypi.org/project/ripgrepy/)


<img src="https://raw.githubusercontent.com/securisec/ripgrepy/master/logo.png" width="150px">

# ripgrepy

`ripgrepy` is a python interface to ripgrep. 
It is written to support Python **3.7+** only and is built on ripgrep version **11.0.1**

For complete usage and details, refer to the docs at 

[Readthedocs](http://ripgrepy.readthedocs.io/en/latest/)

## Instal
Use pip to install
```
pip install ripgrepy
```

## Requirements
`ripgrepy` leverages the system ripgrep to run its commands. So either the standalone binary, rg in $PATH or a path to ripgrep needs to be provided. 

## Usage
Ripgrep is a simple module that allows chaining ripgrep options on top of each other and get the result back. There is a couple of helper methods included to help in parsing, such as the `as_dict` module which shows all valid matches as a dictionary object.

To instantiate the class, use:
```
from ripgrepy import Ripgrepy
# The Ripgrepy class takes two arguments. The regex to search for and the folder path to search in

rg = Ripgrepy('he[l]{2}o', '/some/path/to/files')
```

The syntax for ripgrepy is simliar to that of ripgrep itself. 
```
rg.with_filename().line_number()...run().as_string

# the same can be executed using the rg shorthands

rg.H().n().run().as_string
```
The above is eqivalent to running 
```
rg --with-filename --line-number "he[l]{2}o" /path/to/some/files
```
**Important** `run()` should always be the last method that is being run followed by one of the output methods. If ripgrep options are placed after run, they will not be part of the command being executed. Refer to [Readthedocs](http://ripgrepy.readthedocs.io/en/latest/) for complete documentation. The docs are obtained from ripgreps man pages itself.

#### Output methods
Output can be obtained using the following three properties
- `as_dict`
- `as_json`
- `as_string`

Not all ripgrep output is compitable with `as_dict` and `as_json` output formats
