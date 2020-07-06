# pylint: disable=invalid-name,useless-object-inheritance

import logging
from collections import defaultdict
import gettext

import pycountry
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

from wikitables.models import Field, Row
from wikitables.util import ftag, ustr, guess_type
from wikitables.templates import read_template


log = logging.getLogger('wikitables')

ignore_attrs = ['group="Note"']


class FieldReader(object):
    """ Stateful Field value reader """

    def __init__(self, lang='en'):
        self.lang = lang
        try:
            language_translation = gettext.translation(
                'iso3166', pycountry.LOCALES_DIR, languages=[lang]
            )
            language_translation.install()
        except FileNotFoundError:
            language_translation = gettext
        self.translate_fn = language_translation.gettext

        self._attrs = {} # node attribute state

    def parse(self, node):
        """
        Return generator yielding Field objects for a given node
        """
        self._attrs = {}
        vals = []
        yielded = False

        for x in self._read_parts(node):
            if isinstance(x, Field):
                yielded = True
                x.attrs = self._attrs
                yield x
            else:
                vals.append(ustr(x).strip(' \n\t'))

        joined = ' '.join([x for x in vals if x])
        if joined:
            yielded = True
            yield Field(node, guess_type(joined), self._attrs)

        if not yielded:
            yield Field(node, "", self._attrs)

    def _read_parts(self, n):
        for a in getattr(n, 'attributes', []):
            self._attrs[ustr(a.name)] = ustr(a.value)

        if hasattr(n, 'contents') and hasattr(n.contents, 'nodes'):
            for subnode in n.contents.nodes:
                for x in self._read_parts(subnode):
                    yield x
        else:
            for x in self._read_part(n):
                yield x

    def _read_part(self, node):
        if isinstance(node, Template):
            for x in read_template(node, self.translate_fn):
                yield x
            return
        if isinstance(node, Tag):
            if not self._exclude_tag(node):
                yield node.contents.strip_code()
            return
        if isinstance(node, Wikilink):
            if node.text:
                yield node.text
            else:
                yield node.title
            return

        yield node

    @staticmethod
    def _exclude_tag(node):
        # exclude tag nodes with attributes in ignore_attrs
        n_attrs = [x.strip() for x in node.attributes]
        for a in n_attrs:
            if a in ignore_attrs:
                return True

        # exclude tag nodes without contents
        if not node.contents:
            return True

        return False


class RowReader(object):
    """ Stateful Row reader """

    def __init__(self, tname, head, lang='en'):
        self.head = head
        self.lang = lang
        self._idx = 0
        self._tname = tname
        # track spanned fields across rows
        self._span = {}
        self._nspan = defaultdict(int)
        self._freader = FieldReader(lang)

    def parse(self, *nodes):
        """
        Parse one or more `tr` nodes, yielding wikitables.Row objects
        """
        for n in nodes:
            if not n.contents:
                continue
            row = self._parse(n)
            if not row.is_null:
                yield row

    def _parse(self, node):
        rname = '%s[%s]' % (self._tname, self._idx)
        self._idx += 1
        r = Row(rname, node)
        cols = node.contents.ifilter_tags(matches=ftag('th', 'td'))
        fields = [f for col in cols for f in self._freader.parse(col)]

        for col_name in self.head:
            if self._nspan[col_name]:
                r[col_name] = self._span[col_name]
                self._nspan[col_name] -= 1
                continue

            if not fields:
                log.warning('%s: missing field for column [%s]', r.name, col_name)
                continue

            f = fields.pop(0)
            if 'rowspan' in f.attrs:
                self._span[col_name] = f
                self._nspan[col_name] = int(f.attrs['rowspan'])-1

            r[col_name] = f

        for f in fields:
            log.warning('%s: dropping field from unknown column: %s', r.name, f)

        return r
