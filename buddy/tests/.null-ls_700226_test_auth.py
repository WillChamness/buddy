from buddy.tests._env import ServerSettings
from buddy.tests.http_test import HttpTestCase

class TestSignup(HttpTestCase):
    def test_signup(self):
        username, password = self.generate_random_user()
        
