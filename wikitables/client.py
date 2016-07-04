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
        params = { 'prop': 'revisions',
                   'format': 'json',
                   'action': 'query',
                   'explaintext': '',
                   'titles': title,
                   'rvprop': 'content' }
        r = self.request(method, self.base_url, params=params)
        r.raise_for_status()
        pages = r.json()["query"]["pages"]
        # use key from first result in 'pages' array
        pageid = list(pages.keys())[0]
        if pageid == '-1':
            raise ArticleNotFound('no matching articles returned')

        return pages[pageid]
