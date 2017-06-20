import sys
import json
import logging

log = logging.getLogger('wikitables')

def ftag(*args):
    return lambda node: node.tag in args

def jprint(d):
    if isinstance(d, str):
        d = json.loads(d)
    print(json.dumps(d, indent=2, sort_keys=False, cls=TableJSONEncoder))

def guess_type(s):
    """ attempt to convert string value into numeric type """
    sc = s.replace(',', '') # remove comma from potential numbers

    try:
        return int(sc)
    except ValueError:
        pass

    try:
        return float(sc)
    except ValueError:
        pass

    return s

def ustr(s):
    if sys.version_info < (3, 0):
        #py2
        try:
            return unicode(s).encode('utf-8')
        except UnicodeDecodeError:
            return str(s)
    else:
        return str(s)

class TableJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)
