import requests
from requests import Response
from pydantic import ValidationError
from buddy.tests.http_test import RepoTestCase 
from buddy.tests._env import ServerSettings
from buddy.dtos import AccessTokenDto, UserDto, Login, Signup

class TestGetUser(RepoTestCase):
    def test_get_me(self) -> None:
        responses: list[Response] = []
        for access_token in [self.admin_access, self.access1, self.access2, self.access3]:
            responses.append(self.get(path=f"/users/me", access_token=access_token))

        for response in responses:
            self.assertOk(response.status_code)
            try:
                UserDto.model_validate(response.json())
            except ValidationError:
                self.fail(f"User could not get their own profile. Server response: {response.json()}")


    def test_get_user_by_id(self) -> None:
        responses: list[Response] = []
        for id in range(1, 6): # 1 admin + 3 users + 1 inactive user
            responses.append(self.get(path=f"/users/id/{id}", access_token=self.admin_access))

        for response in responses:
            self.assertOk(response.status_code)
            try:
                UserDto.model_validate(response.json())
            except ValidationError:
                self.fail(f"Could not get user by ID as admin. Server response: {response.json()}")


    def test_get_user_by_username(self) -> None:
        responses: list[Response] = []
        for username in ["admin", "user1", "user2", "user3", "inactiveuser"]:
            responses.append(self.get(path=f"/users/username/{username}", access_token=self.admin_access))

        for response in responses:
            self.assertOk(response.status_code)
            try:
                UserDto.model_validate(response.json())
            except ValidationError:
                self.fail(f"Could not get user by username as admin. Server response: {response.json()}")


    def test_cannot_find_user(self) -> None:
        response: Response = self.get(path=f"/users/id/0", access_token=self.admin_access)

        self.assertNotFound(response.status_code)
        try:
            UserDto.model_validate(response.json())
            self.fail(f"Got user that doesn't exist from the server. Server response: {response.json()}")
        except ValidationError:
            pass

        response = self.get(path=f"/users/username/doesnotexist", access_token=self.admin_access)

        self.assertNotFound(response.status_code)
        try:
            UserDto.model_validate(response.json())
            self.fail(f"Got user that doesn't exist from the server. Server response: {response.json()}")
        except ValidationError:
            pass

            
class TestDeleteUser(RepoTestCase):
    def test_delete_me(self) -> None:
        self.signup(Signup(username="deleteme", password="deleteme"))
        access, _ = self.login(Login(username="deleteme", password="deleteme"))

        response = self.delete(path="/users/delete/me", access_token=access)
        self.assertOk(response.status_code)

        credentials: Login = Login(username="deleteme", password="deleteme")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=f"username={credentials.username}&password={credentials.password}")
        self.assertClientError(response.status_code)
        try:
            AccessTokenDto.model_validate(response.json())
            self.fail(f"Received access token as deleted user. Server response: {response.json()}")
        except ValidationError:
            pass

        refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNone(refresh_token, msg=f"Recieved refresh token as deleted user. Response headers: {response.headers}")

    def test_delete_by_id(self) -> None:
        self.signup(Signup(username="deleteme", password="deleteme"))

        response = self.get(path="/users/username/deleteme", access_token=self.admin_access)
        user_to_delete: UserDto = UserDto.model_validate(response.json())

        response = self.delete(path="/users/delete/id/"+str(user_to_delete.id), access_token=self.admin_access)
        self.assertOk(response.status_code)

        credentials: Login = Login(username="deleteme", password="deleteme")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(ServerSettings.BASE_URL+"/token", headers=headers, data=f"username={credentials.username}&password={credentials.password}")
        self.assertClientError(response.status_code)
        try:
            AccessTokenDto.model_validate(response.json())
            self.fail(f"Received access token as deleted user. Server response: {response.json()}")
        except ValidationError:
            pass

        refresh_token: str|None = response.cookies.get("refresh_token")
        self.assertIsNone(refresh_token, msg=f"Recieved refresh token as deleted user. Response headers: {response.headers}")


class TestUnauthorizedAccess(RepoTestCase):
    def test_unauthorized_get_by_id(self) -> None:
        responses: list[Response] = []
        for id in range(1, 6): # 1 admin + 3 users + 1 inactive user
            responses.append(self.get(path=f"/users/id/{id}", access_token=self.access1))

        for response in responses:
            self.assertClientError(response.status_code)
            try:
                UserDto.model_validate(response.json())
                self.fail(f"Accessed user by ID as non-admin. Server response: {response.json()}")
            except ValidationError:
                pass


    def test_unauthorized_get_by_username(self) -> None:
        responses: list[Response] = []
        for username in ["admin", "user1", "user2", "user3"]:
            responses.append(self.get(path=f"/users/username/{username}", access_token=self.access1))

        for response in responses:
            self.assertClientError(response.status_code)
            try:
                UserDto.model_validate(response.json())
                self.fail(f"Accessed user by username as non-admin. Server response: {response.json()}")
            except ValidationError:
                pass


    def test_unauthorized_delete(self) -> None:
        responses: list[Response] = []
        for id in range(1, 6):
            responses.append(self.delete(path=f"/users/delete/id/{id}", access_token=self.access1))

        for response in responses:
            self.assertClientError(response.status_code)

        self.login(Login(username="admin", password="admin"))
        self.login(Login(username="user1", password="password"))
        self.login(Login(username="user2", password="password"))
        self.login(Login(username="user3", password="password"))



