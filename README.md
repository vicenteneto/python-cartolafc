# Python Cartola FC API

[![PyPi Version](https://img.shields.io/pypi/v/python-cartolafc.svg)](https://pypi.python.org/pypi/python-cartolafc)
[![Downloads](https://img.shields.io/pypi/dm/python-cartolafc.svg)](https://pypi.python.org/pypi/python-cartolafc)
[![Build Status](https://travis-ci.org/vicenteneto/python-cartolafc.svg?branch=master)](https://travis-ci.org/vicenteneto/python-cartolafc)
[![Coverage Status](https://coveralls.io/repos/github/vicenteneto/python-cartolafc/badge.svg?branch=master)](https://coveralls.io/github/vicenteneto/python-cartolafc?branch=master)
[![Requirements Status](https://requires.io/github/vicenteneto/python-cartolafc/requirements.svg?branch=master)](https://requires.io/github/vicenteneto/python-cartolafc/requirements/?branch=master)
[![Development Status](http://img.shields.io/:status-beta-yellowgreen.svg)](https://github.com/vicenteneto/python-cartolafc)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/vicenteneto/python-cartolafc/blob/master/LICENSE)

A python interface into the Cartola FC API.


# Table of contents

- [About this library](#about-this-library)
- [Python versions](#python-versions)
- [Installation](#installation)
- [Example](#example)
- [Contributors](#contributors)
- [Copyright and License](#copyright-and-license)


## About this library

[Cartola FC](https://cartolafc.globo.com/) is a fantasy sport about football, meaning it is a fictional game in which
people create their teams with real life football players. It was released in the year 2005.

Created and maintained by [Globo.com](http://www.globo.com/) and promoted by the cable TV channel
[Sportv](http://sportv.globo.com/), this virtual soccer game already has more than 3 million registered users. At the
start of the 2016 season, the game recorded its best-ever scoring team in a single round in 12 years of fantasy history,
an incredible 2,723,915 users set up their teams for the first round of the 2016 Brazilian Championship.

Thankfully the designers have provided an excellent and complete REST interface. This library wraps up that interface as
more conventional python objects.


## Python versions

The project have been tested and working on Python 2.7, 3.3, 3.4, 3.5 and 3.6.


## Installation

From PyPI:

```bash
    $ pip install Python-CartolaFC
```

Or by downloading the source and running:

```bash
    $ python setup.py install
```

Latest git version:

```bash
    $ pip install git+https://github.com/vicenteneto/python-cartolafc.git#egg=Python-CartolaFC
```


## Example

Python-CartolaFC API is intended to map the objects in CartolaFC (e.g. Athlete, Club, League, Team) into easily
managed Python objects:

```python
>>> import cartolafc
>>> api = cartolafc.Api()
>>> team = api.get_team('falydos-fc')
>>> team.pontos
48.889892578125
>>> team.info.nome
u'Falydos FC'
```

More examples available on Github: [https://github.com/vicenteneto/python-cartolafc/tree/master/examples](https://github.com/vicenteneto/python-cartolafc/tree/master/examples)


## Contributors

Have a bug or a feature request? [Please, open a GitHub issue](https://github.com/vicenteneto/python-cartolafc/issues/new>).

**Vicente Neto (creator)** - <https://github.com/vicenteneto><br/>


## Copyright and license

Copyright 2017-, Vicente Neto. This project is licensed under the [MIT License](https://github.com/vicenteneto/python-cartolafc/blob/master/LICENSE).
