import json
import logging

import mwparserfromhell as mwp

from wikitables.client import Client
from wikitables.readers import RowReader
from wikitables.util import TableJSONEncoder, ftag, ustr


log = logging.getLogger('wikitables')


def import_tables(article, lang='en'):
    client = Client(lang)
    page = client.fetch_page(article)
    body = page['revisions'][0]['*']

    ## parse for tables
    raw_tables = mwp.parse(body).filter_tags(matches=ftag('table'))

    def _table_gen():
        for idx, table in enumerate(raw_tables):
            name = '%s[%s]' % (page['title'], idx)
            yield WikiTable(name, table, lang)

    return list(_table_gen())


class WikiTable():
    """
    Parsed Wikipedia table
    attributes:
     - name(str): Table name in the format <article_name>[<table_index>]
     - head(list): List of parsed column names as strings
     - rows(list): List of <wikitables.Row> objects
    """
    def __init__(self, name, raw_table, lang='en'):
        self.name = ustr(name)
        self.lang = lang
        self.rows = []
        self._head = []
        self._node = raw_table
        self._tr_nodes = raw_table.contents.filter_tags(matches=ftag('tr'))
        self._read_header()
        self._read_rows()

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
        self._read_rows()

    def __repr__(self):
        return "<WikiTable '%s'>" % self.name

    def _log(self, value):
        log.debug('%s: %s', self.name, value)

    def _read_rows(self):
        reader = RowReader(self.name, self._head, self.lang)
        self.rows = list(reader.parse(*self._tr_nodes))
        self._log('parsed %d rows %d cols' % (len(self.rows), len(self._head)))

    def _read_header(self):
        # read header
        header_nodes = self._find_header_flat()
        if not header_nodes:
            header_nodes = self._find_header_row()
        if not header_nodes:
            header_nodes = self._make_default_header()

        for header_node in header_nodes:
            field_name = header_node.contents.strip_code().strip(' ')
            self._head.append(ustr(field_name))

    def _find_header_flat(self):
        """
        Find header elements in a table, if possible. This case handles
        situations where '<th>' elements are not within a row('<tr>')
        """
        nodes = self._node.contents.filter_tags(matches=ftag('th'), recursive=False)
        if not nodes:
            return None
        self._log('found header outside rows (%d <th> elements)' % len(nodes))
        return nodes

    def _find_header_row(self):
        """
        Evaluate all rows and determine header position, based on
        greatest number of 'th' tagged elements
        """
        th_max = 0
        header_idx = 0
        for idx, tr_node in enumerate(self._tr_nodes):
            th_count = len(tr_node.contents.filter_tags(matches=ftag('th')))
            if th_count > th_max:
                th_max = th_count
                header_idx = idx

        if not th_max:
            return None

        self._log('found header at row %d (%d <th> elements)' % \
                    (header_idx, th_max))

        header_row = self._tr_nodes.pop(header_idx)
        return header_row.contents.filter_tags(matches=ftag('th'))

    def _make_default_header(self):
        """
        Return a generic placeholder header based on the tables column count
        """
        td_max = 0

        for tr_node in self._tr_nodes:
            td_count = len(tr_node.contents.filter_tags(matches=ftag('td')))
            if td_count > td_max:
                td_max = td_count

        self._log('creating default header (%d columns)' % td_max)
        return ['column%d' % n for n in range(0, td_max)]
