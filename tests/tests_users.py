import pytest
from jose import jwt
from app import schemas
from app.config import settings



def test_root(client):
    response = client.get("/")
    print(response.json().get('message'))
    assert response.json().get('message') == 'Hello Sebas !!!'
    assert response.status_code == 200


def test_create_user(client):
    # /users/
    response = client.post("/users", json={"email": "test1@gmail.com", "password":'p123'})
    new_user = schemas.UserOut( **response.json() )
    assert new_user.email == "test1@gmail.com"
    assert response.status_code == 201

def test_login_user(client, test_user):
    response = client.post(
        "/login", data={"username":test_user['email'], "password":test_user['password']}
    )
    print(response)
    login_response = schemas.Token(**response.json())

    payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get('user_id')

    assert response.status_code == 200
    assert int(id) == test_user['id']
    assert login_response.token_type == 'bearer'

@pytest.mark.parametrize('email, password, status_code',  [
    ('wrongemail@gmail.com', 'p123', 403),
    ('test1@gmail.com', 'wrongpassword123', 403),
    ('wrongemail@gmail.com', 'wrongpassword123', 403),
    (None, 'p123', 403),
    ('test1@gmail.com', None, 403),
]  )
def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post('/login', data={"username":email, "password": password})
    assert response.status_code == status_code
    assert response.json().get('detail')  == 'Invalid Credentials'

