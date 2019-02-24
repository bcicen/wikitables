# Template readers
import sys

def read_template(node):
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
    return kvs, args

def ustr(s):
    if sys.version_info < (3, 0):
        #py2
        try:
            return unicode(s).encode('utf-8')
        except UnicodeDecodeError:
            return str(s)
    else:
        return str(s)
