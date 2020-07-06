import sys
import json
import logging


log = logging.getLogger('wikitables')


def ftag(*args):
    return lambda node: node.tag in args


def jprint(obj):
    if isinstance(obj, str):
        obj = json.loads(obj)
    print(json.dumps(obj, indent=2, sort_keys=False, cls=TableJSONEncoder))


def guess_type(value):
    """ attempt to convert string value into numeric type """
    num_value = value.replace(',', '') # remove comma from potential numbers

    try:
        return int(num_value)
    except ValueError:
        pass

    try:
        return float(num_value)
    except ValueError:
        pass

    return value


def ustr(value):
    if sys.version_info < (3, 0):
        #py2
        try:
            # pylint: disable=undefined-variable
            return unicode(value).encode('utf-8')
        except UnicodeDecodeError:
            return str(value)
    else:
        return str(value)


class TableJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        return json.JSONEncoder.default(self, o)
