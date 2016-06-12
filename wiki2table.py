import requests
import logging
import json
import mwparserfromhell
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('wikitables')

article_title="List of European cities by population within city limits"

class WikiClient(requests.Session):
    """ """
    base_url = 'https://en.wikipedia.org/w/api.php'

    def __init__(self):
        super(WikiClient, self).__init__()

    def fetch_page(self, title, method='GET'):
        params = { 'prop': 'revisions',
                   'format': 'json',
                   'action': 'query',
                   'explaintext': '',
                   'titles': title,
                   'rvprop': 'content' }
        r = self.request(method, self.base_url, params=params)
        r.raise_for_status()

        return r.json()
    
def import_tables(article):
    client = WikiClient()
    page = client.fetch_page(article)
    for k,v in page['query']['pages'].items():
        full_body = v['revisions'][0]['*']

    ## parse nodes for tables
    raw_tables = mwparserfromhell.parse(full_body).filter_tags(
            matches=lambda node: node.tag == "table")

    return [ read_table(t) for t in raw_tables ]

def read_table(wc):
    data = []
    rows = wc.contents.nodes
    head = read_head(rows.pop(0))
    for row in rows:
        cols = [ read_column(c) for c in row.contents.nodes ]
        if cols:
            data.append( {x:y for x,y in zip(head, cols) })
    return data

def read_head(node):
    head = []
    for th in node.contents.filter_tags(matches=lambda x: x.tag == "th"):
        head.append(th.contents.strip_code().strip(' '))
    return head

def read_column(node):
    vals = [ read_field(f) for f in node.contents.nodes ]
    return ' '.join([ v for v in vals if v ])

def read_field(node):
    if isinstance(node, Template):
        #TODO: handle common wiki templates for type guessing
        if node.name == 'refn':
            return None
        return ' '.join([ str(p) for p in node.params ])
    if isinstance(node, Wikilink):
        return str(node.title)
    return str(node).strip(' \n')

class WikiTable(object):
    def __init__(self, wikicode):
        self._data = {}

    def as_json(self):
        return json.dumps(self._data)

    def _read_head(self):
        pass
