import unittest

import mwparserfromhell as mwp

from wikitables import ftag, WikiTable


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


if __name__ == '__main__':
    unittest.main()
