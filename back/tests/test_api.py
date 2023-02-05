import pytest


class TestMenus:
    url = "/api/v1/menus"

    @pytest.mark.asyncio
    async def test_ctreate_menu(self, client, db):
        menu_data = {
            "title": "menu1",
            "description": "desc1",
        }
        response = await client.post(self.url, json=menu_data)

        assert response.status_code == 201
        assert response.json()["title"] == menu_data["title"]
        assert response.json()["description"] == menu_data["description"]
        assert "submenus_count" in response.json() and response.json()["submenus_count"] == 0
        assert "dishes_count" in response.json() and response.json()["dishes_count"] == 0

    @pytest.mark.asyncio
    async def test_list_menu(self, client, create_menu):
        response = await client.get(self.url)

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["title"] == create_menu["title"]
        assert response.json()[0]["description"] == create_menu["description"]

    @pytest.mark.asyncio
    async def test_get_menu(self, client, db, create_menu):
        menu = await client.get(self.url)

        # print('menu: ', menu.json()[0]['title'])
        response = await client.get(f"{self.url}/{menu.json()[0]['id']}")
        print(response.json()["title"])

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert response.json()["title"] == create_menu["title"]

        error_resp = await client.get(f"{self.url}/0")

        assert error_resp.status_code == 404
        assert error_resp.json() == {"detail": "menu not found"}

    @pytest.mark.asyncio
    async def test_update_menu(self, client, db, create_menu):
        menu = await client.get(self.url)
        menu_id = menu.json()[0]["id"]
        update_data = {"title": "my_menu"}

        response = await client.patch(f"{self.url}/{menu_id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]

        error_resp = await client.patch(f"{self.url}/0", json=update_data)

        assert error_resp.status_code == 404
        assert error_resp.json() == {"detail": "menu not found"}

    @pytest.mark.asyncio
    async def test_delete_menu(self, client, get_menu, db, create_menu):
        menu = await client.get(self.url)
        menu_id = menu.json()[0]["id"]

        response = await client.delete(f"{self.url}/{menu_id}")

        assert response.status_code == 200
        assert response.json() == {
            "status": "true",
            "message": "The menu has been deleted",
        }


class TestSubmenus:
    submenu_data = {
        "title": "submenu1",
        "description": "desc1",
    }

    @pytest.mark.asyncio
    async def test_list_submenu(self, base_url, client):
        response = await client.get(base_url)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_submenu(self, base_url, client):
        response = await client.post(base_url, json=self.submenu_data)

        assert response.status_code == 201
        assert response.json()["title"] == self.submenu_data["title"]
        assert response.json()["description"] == self.submenu_data["description"]

    @pytest.mark.asyncio
    async def test_get_submenu(self, base_url, client):
        submenu_res = await client.post(base_url, json=self.submenu_data)
        submenu_id = submenu_res.json()["id"]
        response = await client.get(f"{base_url}/{submenu_id}")

        assert response.status_code == 200
        assert len(response.json()) == 4
        assert response.json()["dishes_count"] == 0

        error_resp = await client.get(f"{base_url}/0")

        assert error_resp.status_code == 404
        assert error_resp.json() == {"detail": "submenu not found"}

    @pytest.mark.asyncio
    async def test_update_submenu(self, base_url, client):
        update_data = {"title": "new_submenu"}
        submenu_res = await client.post(base_url, json=self.submenu_data)
        submenu_id = submenu_res.json()["id"]
        response = await client.patch(f"{base_url}/{submenu_id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]

        error_resp = await client.get(f"{base_url}/0")

        assert error_resp.status_code == 404
        assert error_resp.json() == {"detail": "submenu not found"}

    @pytest.mark.asyncio
    async def test_delete_submenu(self, base_url, client):
        submenu_res = await client.post(base_url, json=self.submenu_data)
        submenu_id = submenu_res.json()["id"]
        response = await client.delete(f"{base_url}/{submenu_id}")

        assert response.status_code == 200
        assert response.json() == {
            "status": "true",
            "message": "The submenu has been deleted",
        }


class TestDishes:
    dish_data = {
        "title": "dish_1",
        "description": "desc_1",
        "price": "13.5",
    }

    @pytest.mark.asyncio
    async def test_list_dish(self, base_url_dish, client):
        response = await client.get(base_url_dish)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_dish(self, base_url_dish, client):
        response = await client.post(base_url_dish, json=self.dish_data)

        assert response.status_code == 201
        assert response.json()["title"] == self.dish_data["title"]
        assert response.json()["description"] == self.dish_data["description"]

    @pytest.mark.asyncio
    async def test_get_menu(self, base_url_dish, client):
        dish_res = await client.post(base_url_dish, json=self.dish_data)
        dish_id = dish_res.json()["id"]
        response = await client.get(f"{base_url_dish}/{dish_id}")

        assert response.status_code == 200
        assert len(response.json()) == 4
        assert isinstance(response.json()["price"], str)

        error_resp = await client.get(f"{base_url_dish}/0")

        assert error_resp.status_code == 404
        assert error_resp.json() == {"detail": "dish not found"}

    @pytest.mark.asyncio
    async def test_update_dish(self, base_url_dish, client):
        update_data = {
            "title": "new_dish",
            "price": "134.50",
        }
        dish_res = await client.post(base_url_dish, json=self.dish_data)
        dish_id = dish_res.json()["id"]
        response = await client.patch(f"{base_url_dish}/{dish_id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]
        assert response.json()["price"] == update_data["price"]

        error_resp = await client.get(f"{base_url_dish}/0")

        assert error_resp.status_code == 404
        assert error_resp.json() == {"detail": "dish not found"}

    @pytest.mark.asyncio
    async def test_delete_dish(self, base_url_dish, client):
        dish_res = await client.post(base_url_dish, json=self.dish_data)
        dish_id = dish_res.json()["id"]
        response = await client.delete(f"{base_url_dish}/{dish_id}")

        assert response.status_code == 200
        assert response.json() == {
            "status": "true",
            "message": "The dish has been deleted",
        }
