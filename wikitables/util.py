import sys
import json

def ftag(t):
    return lambda node: node.tag == t

def ustr(s):
    if sys.version_info < (3, 0):
        #py2
        return unicode(s).encode('utf-8')
    else:
        return str(s)

class TableJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)
