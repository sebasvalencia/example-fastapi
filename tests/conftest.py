from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app import models
from app.main import app
from app.database import get_db
from app.database import Base
from app.config import settings
from app.oauth2 import create_access_token

from alembic import command

## Create the DB manual on pgAdmin

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# client = TestClient(app)
# @pytest.fixture(scope='module')
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close() 
    

# @pytest.fixture(scope='module')
@pytest.fixture()
def client(session):
    # using SQLAlchemy
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    # run our code before we return our test

    # using Alembic
    # command.upgrade("head")

    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    # run our code after our test finishes
    # command.upgrade("base")



@pytest.fixture
def test_user(client):
    user_data = {"email": "test1@gmail.com", "password":'p123'}
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    print(response.json())
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "test2@gmail.com", "password":'p123'}
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    print(response.json())
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": str(test_user['id'])})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    posts_data = [
        {
            "title": "1 content",
            "content": "1 content",
            "owner_id": test_user['id']
        },
        {
            "title": "2 content",
            "content": "2 content",
            "owner_id": test_user['id']
        },
        {
            "title": "3 content",
            "content": "3 content",
            "owner_id": test_user['id']
        },
        {
            "title": "4 content",
            "content": "4 content",
            "owner_id": test_user2['id']
        }
    ]
    
    def create_post_model(post):
        return models.Post(**post)
    
    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)

    # session.add_all([models.Post(title='1 content', content='1 content', owner_id=test_user['id'])])
    session.commit()
    posts_saved = session.query(models.Post).all()
    return posts_saved
