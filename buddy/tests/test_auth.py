import requests
import random
from pydantic import ValidationError
from buddy.dtos import Signup, Login, AccessTokenDto, PasswordReset
from buddy.tests.http_test import HttpTestCase
from buddy.tests._env import ServerSettings

class TestSignup(HttpTestCase):
    def test_signup(self) -> None:
        credentials: Signup = Signup(username="username" + str(random.randint(1, 10**9)), password="password")
        response = self.post(path="/signup", body=credentials)
        self.assertOk(response.status_code)


class TestLogin(HttpTestCase):
    def test_login(self) -> None:
        credentials: Login = Login(username="user1", password="password")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=f"username={credentials.username}&password={credentials.password}")
        self.assertOk(response.status_code)
        try:
            access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
        except ValidationError:
            self.fail(f"Could not get access token from login. Server response: {response.json()}")

        refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNotNone(refresh_token, msg=f"Refresh token not found in cookies. Response headers: {response.headers}")

    def test_incorrect_username(self) -> None:
        credentials: Login = Login(username="asdf", password="password")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=f"username={credentials.username}&password={credentials.password}")
        self.assertClientError(response.status_code)

        try:
            access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
            self.fail(f"Received access token with incorrect username. Server response: {response.json()}")
        except ValidationError:
            pass

        refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNone(refresh_token, msg=f"Refresh token found in cookies after signing in with incorrect username. Response headers: {response.headers}")

    def test_incorrect_password(self) -> None:
        credentials: Login = Login(username="user1", password="asdf")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=f"username={credentials.username}&password={credentials.password}")
        self.assertClientError(response.status_code)

        try:
            access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
            self.fail(f"Received access token with incorrect password. Server response: {response.json()}")
        except ValidationError:
            pass

        refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNone(refresh_token, msg=f"Refresh token found in cookies after signing in with incorrect password. Server response: {response.json()}")

    def test_inactive_user_request(self) -> None:
        credentials: Login = Login(username="inactiveuser", password="password")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=f"username={credentials.username}&password={credentials.password}")
        self.assertClientError(response.status_code)

        try:
            access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
            self.fail(f"Received access token as inactive user. Server response: {response.json()}")
        except ValidationError:
            pass

        refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNone(refresh_token, msg=f"Refresh token found in cookies after signing in as inactive user. Server response: {response.json()}")


class TestRefresh(HttpTestCase):
    def test_refresh(self) -> None:
        _, refresh_token = self.login(Login(username="user1", password="password"))

        response = requests.post(ServerSettings.BASE_URL+"/refresh", cookies={"refresh_token": refresh_token})
        self.assertOk(response.status_code, msg=f"Server response: {response.json()}")
        try:
            new_access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
        except ValidationError:
            self.fail(f"Could not get access token from login. Server response: {response.json()}")

        new_refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNotNone(new_refresh_token, msg=f"Refresh token not found in cookies. Response headers: {response.headers}")
        self.assertNotEqual(refresh_token, new_refresh_token, msg="Old and new refresh tokens cannot be equal.")


    def test_cannot_reuse_refresh_tokens(self) -> None:
        _, old_refresh_token = self.login(Login(username="user1", password="password"))

        response = requests.post(ServerSettings.BASE_URL+"/refresh", cookies={"refresh_token": old_refresh_token})
        self.assertOk(response.status_code)
        new_refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNotNone(new_refresh_token, msg=f"Refresh token not found in cookies. Response headers: {response.headers}")
        self.assertNotEqual(old_refresh_token, new_refresh_token, msg="Old and new refresh tokens cannot be equal.")

        response = requests.post(ServerSettings.BASE_URL+"/refresh", cookies={"refresh_token": old_refresh_token})
        self.assertClientError(status_code=response.status_code, msg=f"Server did not rotate refresh token. Server response: {response.json()}")
        try:
            new_access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
            self.fail(f"Received new access token from rotated refresh token. Server response: {response.json()}")
        except ValidationError:
            pass

class TestChangePassword(HttpTestCase):
    def test_passwd(self) -> None:
        username: str = "username" + str(random.randint(1, 10**9))
        self.signup(Signup(username=username, password="password"))
        access, _ = self.login(Login(username=username, password="password"))
        response = self.patch(path="/passwd", body=PasswordReset(password="new_password"), access_token=access)

        self.assertOk(response.status_code)
        self.login(Login(username=username, password="new_password"))

        



