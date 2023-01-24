# from .conftest import client



# def get_menu(url, client):
#     return client.get(url).json()[0]


from db import models


class TestMenus:

    url = '/api/v1/menus'

    def test_ctreate_menu(self, client, db):
        menu_data = {
        'title': 'menu1',
        'description': 'desc1'
        }
        response = client.post(self.url, json=menu_data)
        db_data = db.query(models.Menu).first()

        assert response.status_code == 201
        assert response.json()['title'] == db_data.title
        assert response.json()['description'] == db_data.description
        assert 'submenus_count' in response.json() and response.json()['submenus_count'] == 0
        assert 'dishes_count' in response.json() and response.json()['dishes_count'] == 0

    
    def test_list_menu(self, client, create_menu):
        response = client.get(self.url)

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]['title'] == create_menu['title']
        assert response.json()[0]['description'] == create_menu['description']


    def test_get_menu(self, client, db, create_menu):
        menu = db.query(models.Menu).first()
        response = client.get(f'{self.url}/{menu.id}')

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert response.json()['title'] == menu.title

        error_resp = client.get(f'{self.url}/0')

        assert error_resp.status_code == 404
        assert error_resp.json() == {'detail': 'menu not found'}

    
    def test_update_menu(self, client, db, create_menu):
        menu = db.query(models.Menu).first()
        update_data = {'title': 'my_menu'}

        response = client.patch(f'{self.url}/{menu.id}', json=update_data)

        assert response.status_code == 200
        assert response.json()['title'] == update_data['title']

        error_resp = client.patch(f'{self.url}/0', json=update_data)

        assert error_resp.status_code == 404
        assert error_resp.json() == {'detail': 'menu not found'}


    def test_delete_menu(self, client, get_menu, db, create_menu):
        menu = db.query(models.Menu).first()

        response = client.delete(f'{self.url}/{menu.id}')

        assert response.status_code == 200
        assert response.json() == {"status": "true", "message": "The menu has been deleted"}



class TestSubmenus:

    submenu_data = {
        'title': 'submenu1',
        'description': 'desc1'
        }

    def test_list_submenu(self, base_url, client):
        response = client.get(base_url)

        assert response.status_code == 200
        assert response.json() == []


    def test_create_submenu(self, base_url, client):
        response = client.post(base_url, json=self.submenu_data)

        assert response.status_code == 201
        assert response.json()['title'] == self.submenu_data['title']
        assert response.json()['description'] == self.submenu_data['description']

    
    def test_get_submenu(self, base_url, client):
        submenu_id = client.post(base_url, json=self.submenu_data).json()['id']
        response = client.get(f'{base_url}/{submenu_id}')

        assert response.status_code == 200
        assert len(response.json()) == 4
        assert response.json()['dishes_count'] == 0

        error_resp = response = client.get(f'{base_url}/0')

        assert error_resp.status_code == 404
        assert error_resp.json() == {'detail': 'submenu not found'}
        

    def test_update_submenu(self, base_url, client):
        update_data = {'title': 'new_submenu'}
        submenu_id = client.post(base_url, json=self.submenu_data).json()['id']
        response = client.patch(f'{base_url}/{submenu_id}', json=update_data)

        assert response.status_code == 200
        assert response.json()['title'] == update_data['title']

        error_resp = response = client.get(f'{base_url}/0')

        assert error_resp.status_code == 404
        assert error_resp.json() == {'detail': 'submenu not found'}

    
    def test_delete_submenu(self, base_url, client):
        submenu_id = client.post(base_url, json=self.submenu_data).json()['id']
        response = client.delete(f'{base_url}/{submenu_id}')

        assert response.status_code == 200
        assert response.json() == {"status": "true", "message": "The submenu has been deleted"}



class TestDishes:

    dish_data = {
        'title': 'dish_1',
        'description': 'desc_1',
        'price': '13.5'
    }

    def test_list_dish(self, base_url_dish, client):
        response = client.get(base_url_dish)

        assert response.status_code == 200
        assert response.json() == []


    def test_create_dish(self, base_url_dish, client):
        response = client.post(base_url_dish, json=self.dish_data)

        assert response.status_code == 201
        assert response.json()['title'] == self.dish_data['title']
        assert response.json()['description'] == self.dish_data['description']

    
    def test_get_menu(self, base_url_dish, client):
        dish_id = client.post(base_url_dish, json=self.dish_data).json()['id']
        response = client.get(f'{base_url_dish}/{dish_id}')

        assert response.status_code == 200
        assert len(response.json()) == 4
        assert isinstance(response.json()['price'], str)

        error_resp = client.get(f'{base_url_dish}/0')

        assert error_resp.status_code == 404
        assert error_resp.json() == {'detail': 'dish not found'}


    def test_update_dish(self, base_url_dish, client):
        update_data = {
            'title': 'new_dish',
            'price': '134.50'
        }
        dish_id = client.post(base_url_dish, json=self.dish_data).json()['id']
        response = client.patch(f'{base_url_dish}/{dish_id}', json=update_data)

        assert response.status_code == 200
        assert response.json()['title'] == update_data['title']
        assert response.json()['price'] == update_data['price']

        error_resp = client.get(f'{base_url_dish}/0')

        assert error_resp.status_code == 404
        assert error_resp.json() == {'detail': 'dish not found'}


    def test_delete_dish(self, base_url_dish, client):
        dish_id = client.post(base_url_dish, json=self.dish_data).json()['id']
        response = client.delete(f'{base_url_dish}/{dish_id}')

        assert response.status_code == 200
        assert response.json() == {"status": "true", "message": "The dish has been deleted"}