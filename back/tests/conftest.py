import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from fastapi.testclient import TestClient
from app import app
from config import POSTGRES_DB_TEST, POSTGRES_HOST, POSTGRES_HOST_TEST, POSTGRES_PASSWORD, POSTGRES_USER
from db import Base
from db.engine import get_session


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_TEST}/{POSTGRES_DB_TEST}"


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    if not database_exists:
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)

    yield db

    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_session] = lambda: db
    with TestClient(app) as c:
        yield c


def get_first_menu(url, client):
    return client.get(url).json()[0]


@pytest.fixture(scope="function")
def get_menu():
    return get_first_menu


@pytest.fixture(scope="function")
def create_menu(client):
    base_url = "/api/v1/menus"
    menu_data = {
        "title": "menu1",
        "description": "desc1"
    }
    menu = client.post(base_url, json=menu_data)
    
    return menu.json()



@pytest.fixture(scope="function")
def base_url(client):
    base_url = "/api/v1/menus"
    menu = {
        "title": "menu1",
        "description": "desc1"
    }        
    menu_id = client.post(base_url, json=menu).json()['id']

    return f"/api/v1/menus/{menu_id}/submenus"

    # client.delete(f'{base_url}/{menu_id}')


@pytest.fixture(scope="function")
def base_url_dish(client):
    base_url = "/api/v1/menus"
    menu = {
        "title": "menu1",
        "description": "desc1"
    }
    menu_id = client.post(base_url, json=menu).json()['id']

    submenu_url = f"/api/v1/menus/{menu_id}/submenus"
    submenu = {
        "title": "submenu1",
        "description": "desc1"
    }
    submenu_id = client.post(submenu_url, json=submenu).json()['id']

    return f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes"

    # client.delete(f'{base_url}/{menu_id}')