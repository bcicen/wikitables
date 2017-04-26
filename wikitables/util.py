import sys
import json

def ftag(*args):
    return lambda node: node.tag in args

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
