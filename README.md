# wikitables

[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](http://wikitables.readthedocs.org/en/latest/client/) [![PyPI version](https://badge.fury.io/py/wikitables.svg)](https://badge.fury.io/py/wikitables)

Import tables from any Wikipedia article as a dataset in Python

## Installing

```bash
pip install wikitables
```

## Usage

```python
from wikitables import import_tables
tables = import_tables('List of cities in Italy') #returns a list of WikiTable objects
tables[0].json()
```
output:
```json
[
    {
        "City": "Milan",
        "Population January 1, 2014": "6,623,798",
        "Density(inh./km2)": "1,488",
        "Area(km2)": "4,450.11"
    },
    {
        "City": "Naples",
        "Population January 1, 2014": "5,294,546",
        "Density(inh./km2)": "1,699",
        "Area(km2)": "3,116.52"
    },
    ...
```

Full documentation available [here](http://wikitables.readthedocs.org/en/latest/client/)
