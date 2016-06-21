# wikitables
Import any Wikipedia table as a usable dataset in Python

## Installing

```bash
pip install wikitables
```

## Usage

```python
from wikitables import import_tables
tables = import_tables('List of cities in Italy')
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

## Roadmap

Planned improvements include:

* Type guessing for field values
* Improved unit tests
