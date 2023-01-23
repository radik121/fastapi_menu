import pytest
from .test_api import client



@pytest.fixture
def base_url():
    base_url = "/api/v1/menus"
    menu = {
        "title": "menu1",
        "description": "desc1"
    }        
    menu_id = client.post(base_url, json=menu).json()['id']

    yield f"/api/v1/menus/{menu_id}/submenus"

    client.delete(f'{base_url}/{menu_id}')


@pytest.fixture
def base_url_dish():
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

    yield f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes"

    client.delete(f'{base_url}/{menu_id}')    