import json
import unittest

import mwparserfromhell as mwp

from wikitables import ftag, WikiTable


class TestWikiTables(unittest.TestCase):

    def _load(self, source, lang='en'):
        raw_tables = mwp.parse(source).filter_tags(matches=ftag('table'))
        return WikiTable("Test Table", raw_tables[0], lang)

    def _compare(self, table, expected):
        self.assertEqual(len(table.rows), len(expected))
        self.assertSetEqual(set(table.head), set(expected[0].keys()))

        rowsdata = json.loads(table.json())
        for n in range(0, len(expected)):
            self.assertDictEqual(expected[n], rowsdata[n])

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
        expected = [
          {
            "Column 1 header": "Row 1 Column 1",
            "Column 2 header": "Row 1 Column 2"
          },
          {
            "Column 1 header": "Row 2 Column 1",
            "Column 2 header": "Row 2 Column 1"
          }
        ]

        table = self._load(source)
        self._compare(table, expected)

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
        expected = [
          {
            "2018rank": 1,
            "City": "São Paulo",
            "State": "São Paulo",
            "2018Estimate": 12176866,
            "2010Census": 10659386,
            "Change": 14.236092022561152
          },
          {
            "2018rank": 2,
            "City": "Rio de Janeiro",
            "State": "Rio de Janeiro",
            "2018Estimate": 6688927,
            "2010Census": 5940224,
            "Change": 12.603952308869172
          }
        ]

        table = self._load(source)
        self._compare(table, expected)

    def test_flag_template(self):
        source = """
{| class="wikitable"
! Year
! Name
! Nationality
! Citation
|-
| 1978
| [[Carl Djerassi]]
| {{AUT}} / {{USA}}
|  for his work in bioorganic chemistry.
|-
| 1980
| [[Henry Eyring (chemist)|Henry Eyring]]
| {{MEX}} / {{USA}}
|  for his development of absolute rate theory.
|}
"""
        expected = [
          {
            "Year": 1978,
            "Name": "Carl Djerassi",
            "Nationality": "Austria / United States",
            "Citation": "for his work in bioorganic chemistry."
          },
          {
            "Year": 1980,
            "Name": "Henry Eyring",
            "Nationality": "Mexico / United States",
            "Citation": "for his development of absolute rate theory."
          }
        ]

        table = self._load(source)
        self._compare(table, expected)

    def test_flag_template_other_language(self):
        source = """
{| class="wikitable"
! Year
! Name
! Nationality
! Citation
|-
| 1978
| [[Carl Djerassi]]
| {{AUT}} / {{USA}}
|  for his work in bioorganic chemistry.
|-
| 1980
| [[Henry Eyring (chemist)|Henry Eyring]]
| {{MEX}} / {{USA}}
|  for his development of absolute rate theory.
|}
"""
        expected = [
          {
            "Year": 1978,
            "Name": "Carl Djerassi",
            "Nationality": "Österreich / Vereinigte Staaten",
            "Citation": "for his work in bioorganic chemistry."
          },
          {
            "Year": 1980,
            "Name": "Henry Eyring",
            "Nationality": "Mexiko / Vereinigte Staaten",
            "Citation": "for his development of absolute rate theory."
          }
        ]

        table = self._load(source, 'de')
        self._compare(table, expected)

    def test_empty_fields(self):
        source = """
{| class="wikitable sortable" border="1" style="font-size:85%;"
! Archi-<br>tecture
! Bits
! Version
! Intro-<br>duced
! Max #<br>[[operand]]s
! Type
! Design <!-- Design Strategy/Philosophy -->
! [[Processor register|Registers]]<br>(excluding FP/vector)
! Instruction encoding
! [[Branch (computer science)|Branch]] evaluation
! [[Endianness|Endian-<br>ness]]
! Extensions
! Open
! Royalty<br>free
|-
| [[MOS Technology 6502|6502]]
| 8
|
| 1975
| 1
| Register Memory
| CISC
| 3
| Variable <small>(8- to 32-bit)</small>
| Condition register
| Little
|
|
|
|-
| 68000 / [[Motorola 68000 series|680x0]]
| 32
|
| 1979
| 2
| Register Memory
| [[Complex instruction set computer|CISC]]
| 8 data and 8 address
| Variable
| Condition register
| Big
|
|
|
|}
"""

        expected = [
          {
            "Archi-tecture": 6502,
            "Bits": 8,
            "Branch evaluation": "Condition register",
            "Design": "CISC",
            "Endian-ness": "Little",
            "Extensions": "",
            "Instruction encoding": "Variable (8- to 32-bit)",
            "Intro-duced": 1975,
            "Max #operands": 1,
            "Open": "",
            "Registers(excluding FP/vector)": 3,
            "Royaltyfree": "",
            "Type": "Register Memory",
            "Version": ""
          },
          {
            "Archi-tecture": "68000 / 680x0",
            "Bits": 32,
            "Branch evaluation": "Condition register",
            "Design": "CISC",
            "Endian-ness": "Big",
            "Extensions": "",
            "Instruction encoding": "Variable",
            "Intro-duced": 1979,
            "Max #operands": 2,
            "Open": "",
            "Registers(excluding FP/vector)": "8 data and 8 address",
            "Royaltyfree": "",
            "Type": "Register Memory",
            "Version": ""
          }
        ]

        table = self._load(source)
        self._compare(table, expected)


if __name__ == '__main__':
    unittest.main()
