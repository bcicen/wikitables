import json
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

mhead = lambda node: node.tag == "th"
mrow = lambda node: node.tag == "tr"
mcol = lambda node: node.tag == "td"

class WikiTable(object):
    head = []
    rows = []
    """ """
    def __init__(self, name, raw_table):
        self.name = name
        self._read(raw_table)

    @property
    def data(self):
        def _data_gen():
            for row in self.rows:
                yield { x:y for x,y in zip(self.head, row) }
        return list(_data_gen())

    def json(self):
        return json.dumps(self.data)

    def __repr__(self):
        return '<WikiTable %s>' % self.name

    def _read(self, raw_table):
        th_nodes = raw_table.contents.filter_tags(matches=mhead)
        for th in th_nodes:
            val = th.contents.strip_code().strip(' ')
            self.head.append(val)
            raw_table.contents.remove(th)
    
        for row in raw_table.contents.ifilter_tags(matches=mrow):
            cols = row.contents.filter_tags(matches=mcol)
            row = [ self._read_column(c) for c in cols ]
            if row:
                self.rows.append(row)

    def _read_column(self, node):
        def _read_column_fields(fields):
            for f in fields:
                val = self._read_field(f).strip(' \n')
                if val: yield val
        return ' '.join(list(_read_column_fields(node.contents.nodes)))
    
    def _read_field(self, node):
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
