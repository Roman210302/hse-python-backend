import pytest
import base64
from http import HTTPStatus
from faker import Faker

faker = Faker()

def register_new_user(client, user_payload):
    return client.post('/user-register', json=user_payload)

def test_user_registration(client, sample_registration_request, user_sample_info, fake_birthdate, default_password):
    response = register_new_user(client, {
        'username': sample_registration_request.username,
        'name': sample_registration_request.name,
        'birthdate': fake_birthdate,
        'password': default_password,
    })
    json_response = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json_response['username'] == user_sample_info.username
    assert json_response['name'] == user_sample_info.name
    assert json_response['birthdate'] == fake_birthdate

def test_duplicate_user_registration(client, new_user, default_password, fake_birthdate):
    response = register_new_user(client, {
        'username': new_user.username,
        'name': new_user.name,
        'birthdate': fake_birthdate,
        'password': default_password,
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST

@pytest.mark.parametrize("invalid_password", ["short1", "allletters"])
def test_invalid_passwords(client, invalid_password):
    response = register_new_user(client, {
        'username': 'user_example',
        'name': 'example_name',
        'birthdate': str(faker.date_of_birth().isoformat()),
        'password': invalid_password,
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST

def generate_auth_header(credentials):
    return {"Authorization": f"Basic {credentials}"}

def test_fetch_user_data(client, new_user, admin_auth_token):
    response = client.post("/user-get", params={'id': new_user.uid}, headers=generate_auth_header(admin_auth_token))
    json_response = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json_response['username'] == new_user.username
    assert json_response['uid'] == new_user.uid
    assert json_response['role'] == new_user.role

@pytest.mark.parametrize("username, expected_status", [('unknown_user', HTTPStatus.NOT_FOUND), ('', HTTPStatus.NOT_FOUND)])
def test_nonexistent_user(client, admin_auth_token, username, expected_status):
    response = client.post("/user-get", params={'username': username}, headers=generate_auth_header(admin_auth_token))
    assert response.status_code == expected_status

@pytest.mark.parametrize("creds, expected_status", [
    (base64.b64encode("admin:incorrectpassword".encode()).decode(), HTTPStatus.UNAUTHORIZED),
    (base64.b64encode("non_existent_user:validPassword123".encode()).decode(), HTTPStatus.UNAUTHORIZED)
])
def test_user_invalid_credentials(client, new_user, creds, expected_status):
    response = client.post("/user-get", params={'id': new_user.uid}, headers=generate_auth_header(creds))
    assert response.status_code == expected_status

def test_user_promotion(client, new_user, admin_auth_token):
    response = client.post('/user-promote', params={'id': new_user.uid}, headers=generate_auth_header(admin_auth_token))
    assert response.status_code == HTTPStatus.OK

def test_user_promotion_denied(client, new_user, default_password):
    user_creds = base64.b64encode(f"{new_user.username}:{default_password}".encode()).decode()
    response = client.post('/user-promote', params={'id': new_user.uid}, headers=generate_auth_header(user_creds))
    assert response.status_code == HTTPStatus.FORBIDDEN

def test_promotion_of_unknown_user(client, admin_auth_token):
    non_existent_id = faker.random_int(1000, 10000)
    response = client.post('/user-promote', params={'id': non_existent_id}, headers=generate_auth_header(admin_auth_token))
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_both_id_and_username_provided(client, new_user, admin_auth_token):
    response = client.post("/user-get", params={'username': new_user.username, 'id': new_user.uid},
                           headers=generate_auth_header(admin_auth_token))
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_missing_id_and_username(client, admin_auth_token):
    response = client.post("/user-get", headers=generate_auth_header(admin_auth_token))
    assert response.status_code == HTTPStatus.BAD_REQUEST
