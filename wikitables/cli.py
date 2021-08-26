import sys
import json
import logging
from argparse import ArgumentParser

from wikitables.version import version
from wikitables.util import TableJSONEncoder
from wikitables import import_tables
from wikitables.util import jprint


log = logging.getLogger('wikitables')


def main():
    parser = ArgumentParser(description='wikitables v%s' % version)
    parser.add_argument('-l', '--lang',
                        dest='lang',
                        help='article language (default: %(default)s)',
                        default='en')
    parser.add_argument('-p', '--pretty',
                        action='store_true',
                        help='pretty-print json output')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='enable debug output')
    parser.add_argument('article', help='article title')

    args = parser.parse_args()

    if not args.article:
        print('usage: wikitables <article title>')
        sys.exit(1)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        log.debug('debug logging enabled')
    else:
        logging.basicConfig(level=logging.WARN)

    tables = import_tables(args.article, lang=args.lang)
    tables_dict = {table.name: table.rows for table in tables}
    if args.pretty:
        jprint(tables_dict)
    else:
        print(json.dumps(tables_dict, cls=TableJSONEncoder))
