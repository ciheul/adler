import tornado.web
from tornado.httpclient import AsyncHTTPClient

# from mongomanager import PORT as MONGO_PORT


class MongoConnectorMixin(object):
    PORT = 13000

    def __init__(self):
        self.client = AsyncHTTPClient()

    def send(self, resource_url, method='GET', headers=None, body=None):
        """Send data to API provided by MongoManager server."""
        url = self.create_api(resource_url)
        self.client.fetch(url, self.handle_request, method=method,
                          headers=headers, body=body)

    def handle_request(self, response):
        if response.error:
            raise response.error
        else:
            pass

    def create_api(self, url):
        """Helper function to create valid url."""
        return 'http://localhost:{0}{1}'.format(
            str(self.PORT), url if url.startswith('/') else '/' + url)
