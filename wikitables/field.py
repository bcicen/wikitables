import logging
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.wikilink import Wikilink

from wikitables.util import ustr, guess_type

log = logging.getLogger('wikitables')

ignore_attrs = [ 'group="Note"' ]

class Field(object):
    """
    Field within a table row
    attributes:
     - raw(mwparserfromhell.nodes.Node) - Unparsed field Wikicode
     - value(str) - Parsed field value as string
    """
    def __init__(self, node, value):
        self.raw = node
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def __json__(self):
        return self.value

###
# Field value readers
###

def read_fields(node):
    """ Return generator yielding Field objects for a given node """
    vals = []
    for x in _read_parts(node):
        if isinstance(x, Field):
            yield x
        else:
            vals.append(ustr(x).strip(' \n'))

    joined = ' '.join([ x for x in vals if x ])
    yield Field(node, guess_type(joined))

def _read_parts(n):
    if hasattr(n, 'contents') and hasattr(n.contents, 'nodes'):
        for subnode in n.contents.nodes:
            for x in _read_parts(subnode):
                yield x
        return

    for x in _read_part(n):
        yield x

def _read_part(node):
    if isinstance(node, Template):
        for x in _read_template(node):
            yield x
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

###
# Template readers
###

def _read_template(node):
    if node.name == 'refn':
        log.debug('omitting refn subtext from field')
        return
    if node.name == 'change':
        return _read_change_template(node)
    return _read_unknown_template(node)

def _read_unknown_template(node):
    # for unknown templates, concatenate all arg values

    kvs, args = _read_template_params(node)
    return ( ustr(x) for x in args )

def _read_change_template(node):
    params, args = _read_template_params(node)
    args = [ int(ustr(a)) for a in args ]
    yield Field(node, args[0])
    yield Field(node, args[1])
    if params.get('invert') == 'on':
        change = ((args[0] / args[1]) - 1) * 100
    else:
        change = ((args[1] / args[0]) - 1) * 100
    yield Field(node, change)

def _read_template_params(node):
    kvs, args = {}, []
    for p in node.params:
        if '=' in p:
            parts = p.split('=')
            kvs[parts[0]] = '='.join(parts[1:])
        else:
            args.append(p)
    log.debug('parsed template: args=%s params=%s', args, kvs)
    return kvs, args
