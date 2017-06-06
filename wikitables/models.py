import json
import logging
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

from wikitables.util import TableJSONEncoder, ftag, ustr, guess_type

log = logging.getLogger('wikitables')

ignore_attrs = [ 'group="Note"' ]

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
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def __json__(self):
        return self.value

    def _read(self, node):
        def _read_parts():
            for n in node.contents.nodes:
                val = self._read_part(n).strip(' \n')
                if val: yield ustr(val)
        joined = ' '.join(list(_read_parts()))
        return guess_type(joined)

    def _read_part(self, node):
        if isinstance(node, Template):
            if node.name == 'refn':
                log.debug('omitting refn subtext from field')
                return ''
            return self._read_template(node)
        if isinstance(node, Tag):
            if self._exlude_tag(node):
                return ''
            return node.contents.strip_code()
        if isinstance(node, Wikilink):
            if node.text:
                return node.text
            return node.title
        return node

    @staticmethod
    def _exlude_tag(node):
        # exclude tag nodes with attributes in ignore_attrs
        n_attrs = [ x.strip() for x in node.attributes ]
        for a in n_attrs:
            if a in ignore_attrs:
                return True

        # exclude tag nodes without contents
        if not node.contents:
            return True

        return False

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

    def json(self):
        return json.dumps(self, cls=TableJSONEncoder)

    @property
    def is_null(self):
        for k,f in self.items():
            if f.value != '':
                return False
        return True

    @staticmethod
    def _read(head, node):
        cols = node.contents.ifilter_tags(matches=ftag('th', 'td'))
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
        self.rows = []
        self._head = []
        self._node = raw_table
        self._tr_nodes = raw_table.contents.filter_tags(matches=ftag('tr'))
        self._read(raw_table)

    def json(self):
        return json.dumps(self.rows, cls=TableJSONEncoder)

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, val):
        if not isinstance(val, list):
            raise ValueError('table head must be provided as list')
        self._head = val
        self.rows = [ Row(self._head, tr) for tr in self._tr_nodes ]

    def __repr__(self):
        return "<WikiTable '%s'>" % self.name

    def _read(self, raw_table):

        # read header first
        header_nodes = self._find_header_flat()
        if not header_nodes:
            header_nodes = self._find_header_row()

        for th in header_nodes:
            field_name = th.contents.strip_code().strip(' ')
            self._head.append(ustr(field_name))

        # read rows
        for tr in self._tr_nodes:
            row = Row(self._head, tr)
            if not row.is_null:
                self.rows.append(row)

        self._log('parsed %d rows %d cols' % (len(self.rows), len(self._head)))

    def _log(self, s):
        log.debug('%s: %s' % (self.name, s))

    def _find_header_flat(self):
        """
        Find header elements in a table, if possible. This case handles
        situations where '<th>' elements are not within a row('<tr>')
        """
        nodes = self._node.contents.filter_tags(
                    matches=ftag('th'), recursive=False)
        if not nodes:
            return
        self._log('found header outside rows (%d <th> elements)' % len(nodes))
        return nodes

    def _find_header_row(self):
        """
        Evaluate all rows and determine header position, based on
        greatest number of 'th' tagged elements
        """
        th_max = 0
        header_idx = 0
        for idx, tr in enumerate(self._tr_nodes):
            th_count = len(tr.contents.filter_tags(matches=ftag('th')))
            if th_count > th_max:
                th_max = th_count
                header_idx = idx

        self._log('found header at row %d (%d <th> elements)' % \
                    (header_idx, th_max))

        header_row = self._tr_nodes.pop(header_idx)
        return header_row.contents.filter_tags(matches=ftag('th'))
