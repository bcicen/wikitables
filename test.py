import unittest

import mwparserfromhell as mwp

from wikitables import ftag, WikiTable, Client


class TestWikiTables(unittest.TestCase):
    def test_simple_table(self):
        source = """
{| class="wikitable"
|-
! Column 1 header !! Column 2 header
|-
| Row 1 Column 1 || Row 1 Column 2
|-
| Row 2 Column 1 || Row 2 Column 1
|}

"""
        raw_tables = mwp.parse(source).filter_tags(matches=ftag('table'))

        table = WikiTable("Test Table 2", raw_tables[0])

        self.assertEqual(len(table.rows), 2)
        self.assertEqual(list(table.rows[0].keys()), ['Column 1 header', 'Column 2 header'])

    def test_complex_table(self):
        source = """
{| class="wikitable sortable"
! 2018<br>rank 
! [[Municipalities of Brazil|City]]
! [[States of Brazil|State]]
! 2018<br>Estimate
! 2010<br>Census
! Change
|-
! 1
|'''''[[São Paulo]]'''''
| {{flag|São Paulo}}
| {{change|invert=on|12176866|10659386}} 
|-
! 2
| '''''[[Rio de Janeiro]]'''''
| {{flag|Rio de Janeiro}}
| {{change|invert=on|6688927|5940224}}
|}
"""
        raw_tables = mwp.parse(source).filter_tags(matches=ftag('table'))

        table = WikiTable("Test Table 2", raw_tables[0])

        self.assertEqual(len(table.rows), 2)
        self.assertEqual(list(table.rows[0].keys()), ['2018rank', 'City', 'State', '2018Estimate', '2010Census', 'Change'])


if __name__ == '__main__':
    unittest.main()
