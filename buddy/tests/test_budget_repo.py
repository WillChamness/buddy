import random
from pydantic import ValidationError
from requests import Response
from buddy.dtos import BudgetExpenseDto, NewBudgetExpense, UserDto
from buddy.tests.http_test import RepoTestCase
from buddy.dtos import BudgetExpenseDto


class BudgetRepoTestCase(RepoTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        exp1 = NewBudgetExpense(expense_type=f"Expense #{random.randint(1, 10**9)}", amount=100, description=None)
        exp2 = NewBudgetExpense(expense_type=f"Expense #{random.randint(1, 10**9)}", amount=100, description=None)
        exp3 = NewBudgetExpense(expense_type=f"Expense #{random.randint(1, 10**9)}", amount=100, description=None)
        exp4 = NewBudgetExpense(expense_type=f"Expense #{random.randint(1, 10**9)}", amount=200, description=None)

        cls.post(path="/budgeting/expenses", body=exp1, access_token=cls.access1)
        cls.post(path="/budgeting/expenses", body=exp2, access_token=cls.access1)
        cls.post(path="/budgeting/expenses", body=exp3, access_token=cls.access1)
        cls.post(path="/budgeting/expenses", body=exp4, access_token=cls.access2)


class TestCreateExpense(RepoTestCase):
    def test_create_new(self) -> None:
        send_expense = NewBudgetExpense(expense_type="My Expense", amount=800.0, description=None)
        response = self.post(path="/budgeting/expenses/me", body=send_expense, access_token=self.access1)

        self.assertOk(response.status_code, msg=f"Server response: {response.json()}")
        try:
            recv_expense: BudgetExpenseDto = BudgetExpenseDto.model_validate(response.json())
        except ValidationError:
            self.fail(f"Did not recieve an expense after creating a new one. Server response: {response.json()}")
        
        self.assertEqual(send_expense.expense_type, recv_expense.expense_type)

    def test_different_users_create_same_expense(self) -> None:
        expense1 = NewBudgetExpense(expense_type="Some Expense", amount=100, description="This is quite the expense!")
        expense2 = NewBudgetExpense(expense_type="Some Expense", amount=100, description="This is quite the expense!!")

        response1 = self.post(path="/budgeting/expenses/me", body=expense1, access_token=self.access1)
        response2 = self.post(path="/budgeting/expenses/me", body=expense2, access_token=self.access2)

        self.assertOk(response1.status_code)
        self.assertOk(response2.status_code)

        try:
            BudgetExpenseDto.model_validate(response1.json())
            BudgetExpenseDto.model_validate(response2.json())
        except ValidationError:
            self.fail(f"Created similar expenses, but did not get back from the server.")


    def test_user_cannot_create_same_expense(self) -> None:
        expense1 = NewBudgetExpense(expense_type="Some Expense Again", amount=100, description=None)
        expense2 = NewBudgetExpense(expense_type="Some Expense Again", amount=200, description="This is my expense")

        response1 = self.post(path="/budgeting/expenses/me", body=expense1, access_token=self.access1)
        response2 = self.post(path="/budgeting/expenses/me", body=expense2, access_token=self.access1)

        self.assertOk(response1.status_code)
        self.assertClientError(response2.status_code)

        try:
            BudgetExpenseDto.model_validate(response2.json())
            self.fail(f"Cannot create two of the same expenses. Server responses: {response1.json()}; {response2.json()}")
        except ValidationError:
            pass


    def test_cannot_send_bad_expense_type(self) -> None:
        response = self.post(path="/budgeting/expenses/me", body=NewBudgetExpense(expense_type="", amount=20.1, description=None), access_token=self.access1)
        self.assertClientError(response.status_code, msg=f"Server allowed for empty string as expense type")

        try:
            BudgetExpenseDto.model_validate(response.json())
            self.fail(f"Received created BudgetExpenseDto. Server response: {response.json()}")
        except ValidationError:
            pass


    def test_expense_type_case_insensitive(self) -> None:
        expense1 = NewBudgetExpense(expense_type="Some Expense Yet Again", amount=100, description=None)
        expense2 = NewBudgetExpense(expense_type="some expense yet again", amount=200, description=None)
        response1 = self.post(path="/budgeting/expenses/me", body=expense1, access_token=self.access1)
        response2 = self.post(path="/budgeting/expenses/me", body=expense2, access_token=self.access1)

        self.assertOk(response1.status_code)
        self.assertClientError(response2.status_code)

        try:
            BudgetExpenseDto.model_validate(response1.json())
        except ValidationError:
            self.fail()

        try:
            BudgetExpenseDto.model_validate(response2.json())
            self.fail(f"Received BudgetExpenseDto despite case insesnitivity. Server response: {response2.json()}")
        except ValidationError:
            pass
        

class TestReadExpenses(BudgetRepoTestCase):
    def test_user_read(self) -> None:
        responses: list[Response] = []
        for access_token in [self.access1, self.access2, self.access3]:
            responses.append(self.get(path="/budgeting/expenses/me", access_token=access_token))

        for response in responses:
            self.assertOk(response.status_code)

            objects: list = response.json()
            self.assertIsInstance(objects, list, f"Did not receive a list. Server response: {response.json()}")
            for obj in objects:
                try:
                    BudgetExpenseDto.model_validate(obj)
                except ValidationError:
                    self.fail(f"Did not receive list of BudgetExpneseDtos. Server response: {response.json()}")


    def test_get_by_user_id(self) -> None:
        user1_id: int = UserDto.model_validate(self.get(path="/users/me", access_token=self.access1).json()).id
        user2_id: int = UserDto.model_validate(self.get(path="/users/me", access_token=self.access2).json()).id
        user3_id: int = UserDto.model_validate(self.get(path="/users/me", access_token=self.access3).json()).id

        responses: list[Response] = []
        for id in [user1_id, user2_id, user3_id]:
            responses.append(self.get(path=f"/budgeting/expenses/user/{id}", access_token=self.admin_access))

        for response in responses:
            self.assertOk(response.status_code)

            objects: list = response.json()
            self.assertIsInstance(objects, list, f"Did not receive a list. Server response: {response.json()}")
            for obj in objects:
                try:
                    BudgetExpenseDto.model_validate(obj)
                except ValidationError:
                    self.fail(f"Did not receive list of BudgetExpenseDtos. Server response: {response.json()}")


    def test_get_by_expense_type(self) -> None:
        self.post(path="/budgeting/expenses", body=NewBudgetExpense(expense_type="Apartment Rent", amount=1500, description="Montly apartment rent"), 
                  access_token=self.access1)
        self.post(path="/budgeting/expenses", body=NewBudgetExpense(expense_type="Monthly Rent", amount=1300, description="Montly apartment rent"), 
                  access_token=self.access2)
        self.post(path="/budgeting/expenses", body=NewBudgetExpense(expense_type="My Monthly Apartment Rent", amount=1900, description="Montly apartment rent"), 
                  access_token=self.access3)

        
        response: Response = self.get(path="/budgeting/expenses/type/Rent", access_token=self.admin_access)
        objects: list = response.json()
        self.assertIsInstance(objects, list, f"Did not receive a list. Server response: {response.json()}")
        for obj in objects:
            try:
                BudgetExpenseDto.model_validate(obj)
            except ValidationError:
                self.fail(f"Did not receive a list of BudgetExpenseDtos. Server response: {response.json()}")


    def test_expense_type_not_found(self) -> None:
        response: Response = self.get(path="/budgeting/expenses/type/doesnotexist")
        self.assertClientError(response.status_code)
        self.assertNotIsInstance(response.json(), list, f"Received a list from the server. Server response: {response.json()}")



class TestDeleteExpense(BudgetRepoTestCase):
    def test_delete(self) -> None:
        self.post(path="/budgeting/expenses/me", body=NewBudgetExpense(expense_type="deleteme", amount=12.9, description="Delete Me"),
                  access_token=self.access1)

        response: Response = self.delete(path="/budgeting/expenses/me/deleteme", access_token=self.access1)
        self.assertOk(response.status_code)


    def test_delete_nonexistant_expense(self) -> None:
        response = self.delete(path="/budgeting/expenses/me/doesnotexist", access_token=self.access1)
        self.assertClientError(response.status_code)






