# Template readers
import sys
import logging

from wikitables.util import ustr
from wikitables.flag_template import flag_codes

log = logging.getLogger('wikitables')

def read_template(node):
    if node.name == 'refn':
        log.debug('omitting refn subtext from field')
        return []

    for fn in readers:
        a = fn(node)
        if a:
            return a
    return []

def _read_unknown_template(node):
    # for unknown templates, concatenate all arg values
    _, args = _read_template_params(node)
    concat = ' '.join([ ustr(x) for x in args ])
    return [ concat ]

def _read_change_template(node):
    if node.name != 'change':
        return
    params, args = _read_template_params(node)
    args = [ int(ustr(a)) for a in args ]

    if params.get('invert') == 'on':
        change = ((args[0] / args[1]) - 1) * 100
    else:
        change = ((args[1] / args[0]) - 1) * 100

    return [ args[0], args[1], change ]

def _read_flag_template(node):
    # read flag shorthand templates
    sname = ustr(node.name)
    if sname in flag_codes:
        return [flag_codes[sname]]

def _read_template_params(node):
    kvs, args = {}, []
    for p in node.params:
        if '=' in p:
            parts = p.split('=')
            kvs[parts[0]] = '='.join(parts[1:])
        else:
            args.append(p)
    return kvs, args

readers = [
  _read_change_template,
  _read_flag_template,
  _read_unknown_template
]
