import requests
from buddy.tests.http_test import HttpTestCase

class TestServerConnectivity(HttpTestCase):
    def test_connection(self) -> None:
        response: requests.Response = self.get(path="/")
        self.assertOk(response.status_code)
        self.assertEqual(response.json(), "Buddy is running")


