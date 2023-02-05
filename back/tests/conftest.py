import asyncio

import pytest_asyncio
from app import app
from config import PG_DB_TEST, PG_HOST_TEST, POSTGRES_PASSWORD, POSTGRES_USER
from db import Base
from db.engine import get_session
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy_utils import create_database, database_exists

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PG_HOST_TEST}/{PG_DB_TEST}"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    if not database_exists:
        create_database(engine.url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine


@pytest_asyncio.fixture(scope="function")
async def db(db_engine):
    connection = await db_engine.connect()
    transaction = await connection.begin()
    db = AsyncSession(bind=connection)

    yield db

    # db.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def client(db):
    app.dependency_overrides[get_session] = lambda: db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


async def get_first_menu(url, client):
    return await client.get(url).json()[0]


@pytest_asyncio.fixture(scope="function")
def get_menu():
    return get_first_menu


@pytest_asyncio.fixture(scope="function")
async def create_menu(client):
    base_url = "/api/v1/menus"
    menu_data = {
        "title": "menu1",
        "description": "desc1",
    }
    menu = await client.post(base_url, json=menu_data)

    return menu.json()


@pytest_asyncio.fixture(scope="function")
async def base_url(client):
    base_url = "/api/v1/menus"
    menu = {
        "title": "menu1",
        "description": "desc1",
    }
    response = await client.post(base_url, json=menu)
    menu_id = response.json()["id"]

    return f"/api/v1/menus/{menu_id}/submenus"


@pytest_asyncio.fixture(scope="function")
async def base_url_dish(client):
    base_url = "/api/v1/menus"
    menu = {
        "title": "menu1",
        "description": "desc1",
    }
    menu_res = await client.post(base_url, json=menu)
    menu_id = menu_res.json()["id"]

    submenu_url = f"/api/v1/menus/{menu_id}/submenus"
    submenu = {
        "title": "submenu1",
        "description": "desc1",
    }
    submenu_res = await client.post(submenu_url, json=submenu)
    submenu_id = submenu_res.json()["id"]

    return f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes"
