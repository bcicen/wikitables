import sys
import logging
from argparse import ArgumentParser

from wikitables.version import version

log = logging.getLogger('wikitables')

def main():
    parser = ArgumentParser(description='wikitables v%s' % version)
    parser.add_argument('-l','--lang',
                        dest='lang',
                        help='article language (default: %(default)s)',
                        default='en')
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

    from wikitables import import_tables
    from wikitables.util import jprint

    for t in import_tables(args.article, lang=args.lang):
        print(t.name)
        jprint(t.json())
