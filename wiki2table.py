import requests
import logging
import json
from bs4 import BeautifulSoup
from bs4 import element

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('wikitables')

def import_table(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.findAll('h1', {'class': ['firstHeading']})[0].text
    tables = soup.findAll("table", {'class': ['wikitable']})
    return [ WikiTable(t) for t in tables ]

class WikiTable(object):
    omit_classes = set('sortkey', 'reference')

    def __init__(self, raw_table, strip_refs=True):
        self._head = []
        self._data = []
        self._raw_table = raw_table
        self._read()

    def as_json(self):
        return json.dumps(self._data)

    def _read(self):
        rows = self._raw_table.findAll('tr')
        for th in rows.pop(0).findAll('th'):
            self._head.append(self._sanitize(th.text))
        for row in rows:
            self._data.append(self._read_row(row))
                
    def _read_row(self, row):
        nrow = {}
        for idx, td in enumerate(row.findAll('td')):
            nrow[self._head[idx]] = self._strip_ref(td)
        return nrow

    def _parse(self, elem):
        """
        Return a sanitized string of an elements contents,
        minus any omitted classes
        """
        if isinstance(i, element.NavigableString):
            return i
        if i.has_attr('class'):
            if not self.omit_classes.intersection(set(i['class']):
                return i.text
            return None
        return i.text

    def _strip_ref(self, elem):
        parsed = [ self._parse(i) for i in elem.contents ]
        return ' '.join([ i for i in parsed if i ])

    @staticmethod
    def _sanitize(s):
        return s.replace('\n', ' ')


