import logging
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

from wikitables.util import ustr, guess_type
from wikitables.templates import read_template

log = logging.getLogger('wikitables')

ignore_attrs = [ 'group="Note"' ]

class Field(object):
    """
    Field within a table row
    attributes:
     - raw(mwparserfromhell.nodes.Node) - Unparsed field Wikicode
     - value(str) - Parsed field value as string
    """
    def __init__(self, node, value, attrs={}):
        self.raw = node
        self.value = value
        self.attrs = attrs

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def __json__(self):
        return self.value

###
# Field value reader
###

class FieldReader(object):
    def __init__(self):
        self._attrs = {} # node attribute state

    def parse(self, node):
        """
        Return generator yielding Field objects for a given node
        """
        self._attrs = {}
        vals = []
        for x in self._read_parts(node):
            if isinstance(x, Field):
                x.attrs = self._attrs
                yield x
            else:
                vals.append(ustr(x).strip(' \n\t'))

        joined = ' '.join([ x for x in vals if x ])
        if joined:
            yield Field(node, guess_type(joined), self._attrs)

    def _read_parts(self, n):
        for a in getattr(n, 'attributes', []):
            self._attrs[ustr(a.name)] = ustr(a.value)

        if hasattr(n, 'contents') and hasattr(n.contents, 'nodes'):
            for subnode in n.contents.nodes:
                for x in self._read_parts(subnode):
                    yield x
            return

        for x in _read_part(n):
            yield x

def _read_part(node):
    if isinstance(node, Template):
        for x in read_template(node):
            yield Field(node, x)
        return
    if isinstance(node, Tag):
        if not _exclude_tag(node):
            yield node.contents.strip_code()
        return
    if isinstance(node, Wikilink):
        if node.text:
            yield node.text
        else:
            yield node.title
        return

    yield node

def _exclude_tag(node):
    # exclude tag nodes with attributes in ignore_attrs
    n_attrs = [ x.strip() for x in node.attributes ]
    for a in n_attrs:
        if a in ignore_attrs:
            return True

    # exclude tag nodes without contents
    if not node.contents:
        return True

    return False
