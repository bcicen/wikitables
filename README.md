# wikitables

[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](http://wikitables.readthedocs.org/en/latest) [![PyPI version](https://badge.fury.io/py/wikitables.svg)](https://badge.fury.io/py/wikitables) [![Build Status](https://travis-ci.com/bcicen/wikitables.svg?branch=master)](https://travis-ci.com/bcicen/wikitables)

Import tables from any Wikipedia article as a dataset in Python

## Installing

```bash
pip install wikitables
```

## Usage

### Importing

Importing all tables from a given article:
```python
from wikitables import import_tables
tables = import_tables('List of cities in Italy') #returns a list of WikiTable objects
```

To import an article from a different language, simply add the Wikipedia language code as an argument to `import_tables`
```python
tables = import_tables('İtalya\'daki_şehirler_listesi', 'tr') #returns a list of WikiTable objects

```

### Accessing

Iterate over a table's rows:
```python
print(tables[0].name)
for row in tables[0].rows:
    print('{City}: {Area(km2)}'.format(**row))
```

output:
```
List of cities in Italy[0]
Milan: 4,450.11
Naples: 3,116.52
Rome: 3,340.41
Turin: 1,328.40
...
```

Or return the table encoded as JSON:
```python
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

### Table Head

After import, table column names may been modified by setting a new header:

```python
table.head = [ 'newfield1', 'newfield2', 'newfield3' ]
```

This change will be recursively reflected on all of a given tables rows.

### Commandline

Wikitables also comes with a simple cli tool to fetch and output table json:
```bash
wikitables 'List of cities in Italy'
```

### Creating list of DataFrames

```python
from wikitables import import_tables
import pandas as pd


def get_df_from_table_object(table):
    rows = [row for row in table.rows]
    return pd.DataFrame(rows)


def get_list_of_df_of_wiki_article(wiki_title):
    tables = import_tables(wiki_title)
    return [get_df_from_table_object(table) for table in tables]


print(get_list_of_df_of_wiki_article(wiki_title='List of cities in Italy'))
```

output:
```bash
[    Rank         City 2011    Census 2020    Estimate                Change    Region
0      1         Rome        2617175          2856133     9.130379130168986     Lazio
1      2        Milan        1242123          1378689     10.99456334034552  Lombardy
2      3       Naples         962003           959188   -0.2926186300874267  Campania
3      4        Turin         872367           875698   0.38183470947434905  Piedmont
4      5      Palermo         657651           663401    0.8743239195257102    Sicily
..   ...          ...            ...              ...                   ...       ...
139  140  Battipaglia          51133            51005  -0.25032757710284903  Campania
140  141          Rho          50686            50904    0.4300990411553407  Lombardy
141  142       Chieti          54305            50770    -6.509529509253287   Abruzzo
142  143      Scafati          50794            50686   -0.2126235382131747  Campania
143  144    Scandicci          50309            50645    0.6678725476554792   Tuscany

[144 rows x 6 columns]]
```


## Roadmap

Some planned and wishlist features:

* Type guesing from MediaWiki template values
