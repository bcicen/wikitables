import json
import logging
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

from wikitables.util import TableJSONEncoder, ftag, ustr

log = logging.getLogger('wikitables')

class Field(object):
    """
    Field within a table row 
    attributes:
     - raw(mwparserfromhell.nodes.Node) - Unparsed field Wikicode
     - value(str) - Parsed field value as string
    """
    def __init__(self, node):
        self.raw = node
        self.value = self._read(self.raw)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __json__(self):
        return self.value

    def _read(self, node):
        def _read_parts():
            for n in node.contents.nodes:
                val = self._read_part(n).strip(' \n')
                if val: yield ustr(val)
        return ' '.join(list(_read_parts()))
    
    def _read_part(self, node):
        if isinstance(node, Template):
            if node.name == 'refn':
                log.debug('omitting refn subtext from field')
                return ''
            return self._read_template(node)
        if isinstance(node, Tag):
            if node.contents:
                return node.contents.strip_code()
            return ''
        if isinstance(node, Wikilink):
            return node.title
        return node

    @staticmethod
    def _read_template(node):
        """ Concatenate all template values having an integer param name """
        def _is_int(o):
            try:
                int(ustr(o))
                return True
            except ValueError:
                return False

        vals = [ ustr(p.value) for p in node.params if _is_int(p.name) ]
        return ' '.join(vals)

class Row(dict):
    """
    Single WikiTable row, mapping a field name(str) to wikitables.Field obj
    """
    def __init__(self, *args, **kwargs):
        head = args[0]
        self.raw = args[1]
        super(Row, self).__init__(self._read(head, self.raw))

    @property
    def is_null(self):
        for k,f in self.items():
            if f.value != '':
                return False
        return True

    @staticmethod
    def _read(head, node):
        cols = node.contents.ifilter_tags(matches=ftag('td'))
        return zip(head, [ Field(c) for c in cols ])

class WikiTable(object):
    """ 
    Parsed Wikipedia table
    attributes:
     - name(str): Table name in the format <article_name>[<table_index>] 
     - head(list): List of parsed column names as strings
     - rows(list): List of <wikitables.Row> objects
    """
    def __init__(self, name, raw_table):
        self.name = ustr(name)
        self.head = []
        self.rows = []
        self._read(raw_table)

    def json(self):
        return json.dumps(self.rows, cls=TableJSONEncoder)

    def __repr__(self):
        return "<WikiTable '%s'>" % self.name

    def _read(self, raw_table):
        th_nodes = raw_table.contents.filter_tags(matches=ftag('th'))
        for th in th_nodes:
            field_name = th.contents.strip_code().strip(' ')
            self.head.append(ustr(field_name))
            raw_table.contents.remove(th)
        log.debug('parsed %d columns from table %s' % \
                (len(th_nodes), self.name))
    
        for tr in raw_table.contents.ifilter_tags(matches=ftag('tr')):
            row = Row(self.head, tr)
            if not row.is_null:
                self.rows.append(row)
        log.debug('parsed %d rows from table %s' % \
                (len(self.rows), self.name))
