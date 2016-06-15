import requests

class ArticleNotFound(RuntimeError):
    """ Article query returned no results """

class Client(requests.Session):
    """ """
    base_url = 'https://en.wikipedia.org/w/api.php'

    def __init__(self):
        super(WikiClient, self).__init__()

    def fetch_page(self, title, method='GET'):
        params = { 'prop': 'revisions',
                   'format': 'json',
                   'action': 'query',
                   'explaintext': '',
                   'titles': title,
                   'rvprop': 'content' }
        r = self.request(method, self.base_url, params=params)
        r.raise_for_status()
        pages = r.json()['query']['pages']
        if '-1' in pages:
            raise ArticleNotFound('no matching articles returned')

        return pages
