import requests
import logging
import json
import mwparserfromhell
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('wikitables')

article_title="List of European cities by population within city limits"

mtables = lambda node: node.tag == "table"
mhead = lambda node: node.tag == "th"
mrow = lambda node: node.tag == "tr"
mcol = lambda node: node.tag == "td"

class ArticleNotFound(RuntimeError):
    """ Article query returned no results """

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
        pages = r.json()['query']['pages']
        if '-1' in pages:
            raise ArticleNotFound('no matching articles returned')

        return pages
    
def import_tables(article):
    client = WikiClient()
    pages = client.fetch_page(article)
    for k,v in pages.items():
        body = v['revisions'][0]['*']

    ## parse nodes for tables
    raw_tables = mwparserfromhell.parse(body).filter_tags(matches=mtables)

    return [ read_table(t) for t in raw_tables ]

def read_table(table):
    data = []
    head = []

    # read head
    th_nodes = table.contents.filter_tags(matches=mhead)
    for th in th_nodes:
        val = th.contents.strip_code().strip(' ')
        head.append(val)
        table.contents.remove(th)

    for row in table.contents.ifilter_tags(matches=mrow):
        cols = row.contents.filter_tags(matches=mcol)
        vals = [ read_column(c) for c in cols ]
        if vals:
            data.append( {x:y for x,y in zip(head, vals) })

    return data

def read_column(node):
    print(node.contents)
    try:
        vals = [ read_field(f).strip(' \n') for f in node.contents.nodes ]
    except Exception as e:
        raise Exception(e)
    return ' '.join([ v for v in vals if v ])

def read_field(node):
    if isinstance(node, Template):
        #TODO: handle common wiki templates for type guessing
        if node.name == 'refn':
            return ''
        return ' '.join([ str(p) for p in node.params ])
    if isinstance(node, Tag):
        return ''
    if isinstance(node, Wikilink):
        return str(node.title)
    return str(node)

class WikiTable(object):
    def __init__(self, wikicode):
        self._data = {}

    def as_json(self):
        return json.dumps(self._data)

    def _read_head(self):
        pass
