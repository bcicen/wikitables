# Template readers
import sys
import logging

import pycountry

from wikitables.util import ustr
from wikitables.models import Field


log = logging.getLogger('wikitables')


def read_template(node, translate_fn):
    if node.name == 'refn':
        log.debug('omitting refn subtext from field')
        return []

    for fn in _tmpl_readers:
        a = fn(node, translate_fn)
        if a:
            return a
    return []


def _read_unknown_template(node, translate_fn):
    # for unknown templates, concatenate all arg values
    _, args = _read_template_params(node)
    concat = ' '.join([ ustr(x) for x in args ])
    return [ concat ]


def _read_change_template(node, ltranslate_fn):
    if node.name != 'change':
        return
    params, args = _read_template_params(node)
    args = [ int(ustr(a)) for a in args ]

    if params.get('invert') == 'on':
        change = ((args[0] / args[1]) - 1) * 100
    else:
        change = ((args[1] / args[0]) - 1) * 100

    return [ Field(node, args[0]), Field(node, args[1]), Field(node, change) ]


def _read_flag_template(node, translate_fn):
    # read flag shorthand templates
    sname = ustr(node.name)
    try:
        country = pycountry.countries.lookup(sname)
        return [translate_fn(country.name)]
    except LookupError:
        pass


def _read_template_params(node):
    kvs, args = {}, []
    for p in node.params:
        if '=' in p:
            parts = p.split('=')
            kvs[parts[0]] = '='.join(parts[1:])
        else:
            args.append(p)
    return kvs, args

_tmpl_readers = [
  _read_change_template,
  _read_flag_template,
  _read_unknown_template
]
