import logging
import requests


log = logging.getLogger(__name__)


class ArticleNotFound(RuntimeError):
    """ Article query returned no results """


class Client(requests.Session):
    """ Mediawiki API client """

    def __init__(self, lang="en"):
        super(Client, self).__init__()
        self.base_url = 'https://' + lang + '.wikipedia.org/w/api.php'

    def fetch_page(self, title, method='GET'):
        """ Query for page by title """
        params = {
            'prop': 'revisions',
            'format': 'json',
            'action': 'query',
            'explaintext': '',
            'titles': _parse_title(title),
            'rvprop': 'content',
        }
        req = self.request(method, self.base_url, params=params)
        req.raise_for_status()
        pages = req.json()["query"]["pages"]
        # use key from first result in 'pages' array
        page_id = list(pages.keys())[0]
        if page_id == '-1':
            raise ArticleNotFound('no matching articles returned')

        return pages[page_id]

def _parse_title(s):
    # extract title from, potentially, a URL
    return s.split('/')[-1].split('#')[0].split('?')[0]
