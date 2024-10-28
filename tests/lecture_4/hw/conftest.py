import pytest
from fastapi.testclient import TestClient
from faker import Faker
import base64
from http import HTTPStatus
from pydantic import SecretStr
from lecture_4.demo_service.api.contracts import UserResponse, RegisterUserRequest
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserInfo, UserRole

app = create_app()
faker = Faker()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def birthdate():
    return faker.date_time().isoformat()


@pytest.fixture()
def password():
    return "qwerty123456"


@pytest.fixture()
def admin_creds():
    return base64.b64encode("admin:secretqwerty123456".encode()).decode()


@pytest.fixture()
def user_info(birthdate, password):
    return UserInfo(
        username="Nagibator228",
        name="Legender",
        birthdate=birthdate,
        role=UserRole.USER,
        password=SecretStr(password)
    )


@pytest.fixture()
def user(client, password, birthdate, user_info):
    response = client.post('/user-register', json={
        'username': user_info.username,
        'name': user_info.name,
        'birthdate': birthdate,
        'password': password,
    })
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    return UserResponse(
        uid=data['uid'],
        username=data['username'],
        name=data['name'],
        birthdate=data['birthdate'],
        role=data['role']
    )


@pytest.fixture()
def register_user_request(user_info, password):
    return RegisterUserRequest(
        username=user_info.username,
        name=user_info.name,
        birthdate=user_info.birthdate,
        password=password
    )