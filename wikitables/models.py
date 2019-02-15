import json
import logging

from wikitables.field import read_fields
from wikitables.util import TableJSONEncoder, ftag, ustr

log = logging.getLogger('wikitables')

class Row(dict):
    """
    Single WikiTable row, mapping a field name(str) to wikitables.Field obj
    """
    def __init__(self, *args, **kwargs):
        head = args[0]
        self.raw = args[1]
        self._read(head)

    def json(self):
        return json.dumps(self, cls=TableJSONEncoder)

    @property
    def is_null(self):
        for k,f in self.items():
            if f.value != '':
                return False
        return True

    def _read(self, head):
        cols = self.raw.contents.ifilter_tags(matches=ftag('th', 'td'))
        for c in cols:
            for f in read_fields(c):
                if len(self) >= len(head):
                    log.warn('dropping field from unknown column: %s' % f)
                    continue
                col_name = head[len(self)]
                self[col_name] = f

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
            if tr.contents:
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
