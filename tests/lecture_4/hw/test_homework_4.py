import pytest
import base64
from http import HTTPStatus
from faker import Faker

faker = Faker()


def register_user(client, user_data):
    return client.post('/user-register', json=user_data)


def test_register_user(client, register_user_request, user_info, birthdate, password):
    response = register_user(client, {
        'username': register_user_request.username,
        'name': register_user_request.name,
        'birthdate': birthdate,
        'password': password,
    })
    json = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json['username'] == user_info.username
    assert json['name'] == user_info.name
    assert json['birthdate'] == birthdate


def test_register_existed_user(client, user, password, birthdate):
    response = register_user(client, {
        'username': user.username,
        'name': user.name,
        'birthdate': birthdate,
        'password': password,
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("password", ["short123", "password_without_number"])
def test_invalid_password(client, password):
    response = register_user(client, {
        'username': 'user1',
        'name': 'user1',
        'birthdate': str(faker.date_time().isoformat()),
        'password': password,
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST


def auth_header(credentials):
    return {"Authorization": f"Basic {credentials}"}


def test_get_user(client, user, admin_credentials):
    response = client.post("/user-get", params={'id': user.uid}, headers=auth_header(admin_credentials))
    json = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json['username'] == user.username
    assert json['uid'] == user.uid
    assert json['role'] == user.role


@pytest.mark.parametrize("username, expected_status", [('unknown', HTTPStatus.NOT_FOUND), ('', HTTPStatus.NOT_FOUND)])
def test_not_existed_user(client, admin_credentials, username, expected_status):
    response = client.post("/user-get", params={'username': username}, headers=auth_header(admin_credentials))
    assert response.status_code == expected_status


@pytest.mark.parametrize("creds, expected_status", [
    (base64.b64encode("admin:wrongpassword".encode()).decode(), HTTPStatus.UNAUTHORIZED),
    (base64.b64encode("invalid_user:strongpassword123".encode()).decode(), HTTPStatus.UNAUTHORIZED)
])
def test_user_invalid_creds(client, user, creds, expected_status):
    response = client.post("/user-get", params={'id': user.uid}, headers=auth_header(creds))
    assert response.status_code == expected_status


def test_user_promote(client, user, admin_credentials):
    response = client.post('/user-promote', params={'id': user.uid}, headers=auth_header(admin_credentials))
    assert response.status_code == HTTPStatus.OK


def test_user_promote_forbid(client, user, password):
    creds = base64.b64encode(f"{user.username}:{password}".encode()).decode()
    response = client.post('/user-promote', params={'id': user.uid}, headers=auth_header(creds))
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_user_promote_unknown_user(client, admin_credentials):
    random_id = faker.random_int(1000, 10000)
    response = client.post('/user-promote', params={'id': random_id}, headers=auth_header(admin_credentials))
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_both_username_and_id_provided(client, user, admin_credentials):
    response = client.post("/user-get", params={'username': user.username, 'id': user.uid},
                           headers=auth_header(admin_credentials))
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_neither_username_nor_id_provided(client, admin_credentials):
    response = client.post("/user-get", headers=auth_header(admin_credentials))
    assert response.status_code == HTTPStatus.BAD_REQUEST