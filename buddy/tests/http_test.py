import unittest
import requests
import random
from buddy.tests._env import ServerSettings
from buddy.dtos import AccessTokenDto, Signup, Login
from pydantic import BaseModel, ValidationError

class HttpTestCase(unittest.TestCase):
    def get(self, *, path: str="", access_token: AccessTokenDto|None=None) -> requests.Response:
        headers: dict[str, str] = {}
        if access_token is not None:
            headers["Authorization"] = "Bearer " + access_token.access_token

        return requests.get(ServerSettings.BASE_URL + path, headers=headers)

    def post(self, *, path: str="", body: BaseModel|None=None, access_token: AccessTokenDto|None=None) -> requests.Response:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if access_token is not None:
            headers["Authorization"] = "Bearer " + access_token.access_token

        if body is None:
            return requests.post(ServerSettings.BASE_URL + path, headers=headers)
        else:
            return requests.post(ServerSettings.BASE_URL + path, json=dict(body), headers=headers)

    def put(self, *, path: str="", body: BaseModel|None=None, access_token: AccessTokenDto|None=None) -> requests.Response:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if access_token is not None:
            headers["Authorization"] = "Bearer " + access_token.access_token

        if body is None:
            return requests.put(ServerSettings.BASE_URL + path, headers=headers)
        else:
            return requests.put(ServerSettings.BASE_URL + path, json=dict(body), headers=headers)

    def patch(self, *, path: str="", body: BaseModel|None=None, access_token: AccessTokenDto|None=None) -> requests.Response:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if access_token is not None:
            headers["Authorization"] = "Bearer " + access_token.access_token

        if body is None:
            return requests.patch(ServerSettings.BASE_URL + path, headers=headers)
        else:
            return requests.patch(ServerSettings.BASE_URL + path, json=dict(body), headers=headers)

    def delete(self, *, path: str="", body: BaseModel|None=None, access_token: AccessTokenDto|None=None) -> requests.Response:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if access_token is not None:
            headers["Authorization"] = "Bearer " + access_token.access_token

        if body is None:
            return requests.delete(ServerSettings.BASE_URL + path, headers=headers)
        else:
            return requests.delete(ServerSettings.BASE_URL + path, json=dict(body), headers=headers)

    def assertOk(self, status_code: int, msg: str|None=None) -> None:
        if msg is None:
            msg = f"{status_code} is not an OK status code"
        self.assertTrue(200 <= status_code and status_code <= 299, msg=msg)

    def assertClientError(self, status_code: int, msg: str|None=None) -> None:
        if msg is None:
            f"{status_code} is not a client error status code"
        self.assertTrue(400 <= status_code and status_code <= 499, msg=msg)

    def assertServerError(self, status_code: int, msg: str|None=None) -> None:
        if msg is None:
            f"{status_code} is not a server error status code"
        self.assertTrue(500 <= status_code and status_code <= 599, msg=msg)

    @staticmethod
    def signup(credentials: Signup) -> None:
        response: requests.Response = requests.post(url=ServerSettings.BASE_URL+"/signup", json=dict(credentials))
        assert 200 <= response.status_code and response.status_code <= 299

    @staticmethod
    def login(credentials: Login) -> tuple[AccessTokenDto, str]:
        """
        Args: 
            credentials (Login): The username and password to be converted into x-www-form-urlencoded data

        Returns:
            (AccessTokenDto, str): The access token object and refresh token string
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = f"username={credentials.username}&password={credentials.password}" 
        response: requests.Response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=data)
        assert 200 <= response.status_code and response.status_code <= 299

        access_token: AccessTokenDto = AccessTokenDto.model_validate(response.json())
        refresh_token: str|None = response.cookies.get("refresh_token")
        assert refresh_token is not None

        return (access_token, refresh_token)

