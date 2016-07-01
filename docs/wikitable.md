# wikitables.WikiTable

Parsed Wikipedia table

**Attributes**:

* name (str): Table name in the format <article_name>[<table_index>]
* head (list): List of parsed column names as strings
* rows (list): List of <wikitables.Row> objects

# wikitables.Row

Single WikiTable row as dictionary, mapping a field name(str) to wikitables.Field object

**Methods**

## is_null

Whether a row is populated only with empty fields

**Returns** (bool)

# wikitables.Field

Single field within a table row

**Attributes**:

* value (str): Parsed field value as string
* raw (mwparserfromhell.nodes.Node): Unparsed field Wikicode
