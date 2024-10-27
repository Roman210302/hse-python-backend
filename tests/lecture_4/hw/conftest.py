import pytest
from faker import Faker
import base64
from fastapi.testclient import TestClient
from http import HTTPStatus
from pydantic import SecretStr
from lecture_4.demo_service.api.contracts import UserResponse, RegisterUserRequest
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserInfo, UserRole

app = create_app()
faker = Faker()

@pytest.fixture
def client():
    with TestClient(app) as test_client_instance:
        yield test_client_instance

@pytest.fixture
def fake_birthdate():
    return faker.date_of_birth().isoformat()

@pytest.fixture
def default_password():
    return "qwerty123456"

@pytest.fixture
def admin_auth_token():
    return base64.b64encode("admin:superSecretAdminPassword123".encode()).decode()

@pytest.fixture
def user_sample_info(fake_birthdate, default_password):
    return UserInfo(
        username="test_user",
        name="Test User",
        birthdate=fake_birthdate,
        role=UserRole.USER,
        password=SecretStr(default_password)
    )

@pytest.fixture
def new_user(client, fake_birthdate, default_password, user_sample_info):
    response = client.post('/user-register', json={
        'username': user_sample_info.username,
        'name': user_sample_info.name,
        'birthdate': fake_birthdate,
        'password': default_password,
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

@pytest.fixture
def sample_registration_request(user_sample_info, default_password):
    return RegisterUserRequest(
        username=user_sample_info.username,
        name=user_sample_info.name,
        birthdate=user_sample_info.birthdate,
        password=default_password
    )
