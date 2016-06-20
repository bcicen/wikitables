import json
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

def ftag(t):
    return lambda node: node.tag == t

class Field(object):
    def __init__(self, node):
        self.raw = node
        self.value = self._read(self.raw)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def _read(self, node):
        def _read_parts():
            for n in node.contents.nodes:
                val = self._read_part(n).strip(' \n')
                if val: yield val
        return ' '.join(list(_read_parts()))
    
    def _read_part(self, node):
        if isinstance(node, Template):
            if node.name == 'refn':
                return ''
            return self._read_template(node)
        if isinstance(node, Tag):
            if node.contents:
                return node.contents.strip_code()
            return ''
        if isinstance(node, Wikilink):
            return str(node.title)
        return str(node)

    @staticmethod
    def _read_template(node):
        """ Concatenate all template values having an integer param name """
        def _is_int(o):
            try:
                int(str(o))
                return True
            except ValueError:
                return False

        vals = [ str(p.value) for p in node.params if _is_int(p.name) ]
        return ' '.join(vals)

class Row(list):
    def __init__(self, *args, **kwargs):
        self.raw = args[0]
        super(Row, self).__init__(self._read(self.raw))

    @property
    def is_null(self):
        for f in self.__iter__():
            if f.value != '':
                return False
        return True

    @staticmethod
    def _read(node):
        cols = node.contents.ifilter_tags(matches=ftag('td'))
        return [ Field(c) for c in cols ]

class WikiTable(object):
    """ 
    Parsed Wikipedia table
    attributes:
     - name(str): Table name in the format <article_name>[<table_index>] 
     - data(list): List of dicts(rows) containing parsed column names and values
     - head(list): List of parsed column names
     - rows(list): List of parsed rows
    """
    def __init__(self, name, raw_table):
        self.name = name
        self.head = []
        self.rows = []
        self._read(raw_table)

    @property
    def data(self):
        def _data_gen():
            for row in self.rows:
                yield { x:y for x,y in zip(self.head, row) }
        return list(_data_gen())

    def json(self):
        return json.dumps(self.data, cls=WtJsonEncoder)

    def __repr__(self):
        return "<WikiTable '%s'>" % self.name

    def _read(self, raw_table):
        th_nodes = raw_table.contents.filter_tags(matches=ftag('th'))
        for th in th_nodes:
            self.head.append(th.contents.strip_code().strip(' '))
            raw_table.contents.remove(th)
    
        for tr in raw_table.contents.ifilter_tags(matches=ftag('tr')):
            row = Row(tr)
            if not row.is_null:
                self.rows.append(row)
