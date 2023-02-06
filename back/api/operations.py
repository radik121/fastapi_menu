import json

from db.models import Dish, Menu, Submenu
from schemas.dish import DishCreate, DishUpdate
from schemas.menu import MenuCreate, MenuUpdate
from schemas.submenu import SubmenuCreate, SubmenuUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .cache import cache
from .service import ServiceExc, ServiceQuery


class MenuCrud:
    """Requests by menu"""

    async def get_list(self, db: Session):
        key = "menus_list"
        cache_menus = await cache.get(key)

        if cache_menus:
            return cache_menus

        query = await db.execute(ServiceQuery.select_menu_list())
        result = query.all()

        menus = []
        for i in result:
            item = None
            item = i[0]
            item.submenus_count = i[1]
            item.dishes_count = i[2]
            menus.append(item)

        if menus:
            await cache.set(key, menus)

        return menus

    async def get_id_menu(self, menu_id: int, db: Session):
        key = f"menu_{menu_id}"
        cache_menu = await cache.get(key)

        if cache_menu:
            return cache_menu

        query = await db.execute(ServiceQuery.select_menu(menu_id))
        result = query.first()

        if result:
            menu = result[0]
            menu.submenus_count = result[1]
            menu.dishes_count = result[2]

            if menu:
                await cache.set(key, menu)

            return menu
        else:
            ServiceExc.not_found_404("menu")

    async def create(self, menu_data: MenuCreate, db: Session):
        try:
            await cache.delete_one(["menus_list"])
            menu_db = Menu(**menu_data.dict())
            db.add(menu_db)
            await db.commit()
            await db.refresh(menu_db)
            return menu_db
        except IntegrityError:
            ServiceExc.unique_violation("Menu")

    async def update(self, menu_id: int, menu_data: MenuUpdate, db: Session):
        key = [f"menu_{menu_id}", "menus_list"]

        query = await db.execute(ServiceQuery.select_menu(menu_id))
        result = query.first()

        if result:
            menu = result[0]
            menu.submenus_count = result[1]
            menu.dishes_count = result[2]
            menu.title = menu_data.title if menu_data.title else menu.title
            menu.description = menu_data.description if menu_data.description else menu.description
            db.add(menu)
            await db.commit()
            await db.refresh(menu)

            await cache.delete_one(key)
            return menu
        else:
            ServiceExc.not_found_404("menu")

    async def delete(self, menu_id: int, db: Session):
        query = await db.execute(ServiceQuery.select_or_delete_menu(menu_id, "select"))
        result = query.first()

        if not result:
            ServiceExc.not_found_404("menu")

        await db.execute(ServiceQuery.select_or_delete_menu(menu_id, "delete"))
        await db.commit()

        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"dish_{menu_id}",
        ]
        await cache.delete_all(key)

        return {
            "status": "true",
            "message": "The menu has been deleted",
        }


class SubmenuCrud:
    """Requests by submenu"""

    async def get_list(self, menu_id: int, db: Session):
        key = f"submenu_{menu_id}"
        cache_submenus = await cache.get(key)

        if cache_submenus:
            return cache_submenus

        query = await db.execute(ServiceQuery.select_submenu_list(menu_id))
        result = query.all()

        submenus = []
        for i in result:
            item = None
            item = i[0]
            item.dishes_count = i[1]
            submenus.append(item)

        if submenus:
            await cache.set(key, submenus)

        return submenus

    async def get_id_submenu(self, menu_id: int, submenu_id: int, db: Session):
        key = f"submenu_{menu_id}_{submenu_id}"
        cache_submenu = await cache.get(key)

        if cache_submenu:
            return cache_submenu

        query = await db.execute(ServiceQuery.select_submenu(menu_id, submenu_id))
        result = query.first()

        if not result:
            ServiceExc.not_found_404("submenu")

        submenu = result[0]
        submenu.dishes_count = result[1]

        if submenu:
            await cache.set(key, submenu)

        return submenu

    async def create(self, menu_id: int, submenu_data: SubmenuCreate, db: Session):
        try:
            key = [f"menu_{menu_id}", "menus_list", f"submenu_{menu_id}"]
            await cache.delete_one(key)

            result = await db.execute(ServiceQuery.select_or_delete_menu(menu_id, "select"))
            menu = result.first()

            if not menu:
                ServiceExc.not_found_404("menu")

            submenu_db = Submenu(menu_id=menu_id, **dict(submenu_data))  # type: ignore[call-arg]
            db.add(submenu_db)
            await db.commit()
            await db.refresh(submenu_db)
            return submenu_db
        except IntegrityError:
            ServiceExc.unique_violation("Submenu")

    async def update(self, menu_id: int, submenu_id: int, submenu_data: SubmenuUpdate, db: Session):
        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{submenu_id}",
        ]
        await cache.delete_one(key)

        query = await db.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "select"))
        submenu = query.scalars().first()

        if submenu:
            submenu.title = submenu_data.title if submenu_data.title else submenu.title
            submenu.description = submenu_data.description if submenu_data.description else submenu.description
            db.add(submenu)
            await db.commit()
            await db.refresh(submenu)
            return submenu
        else:
            ServiceExc.not_found_404("submenu")

    async def delete(self, menu_id: int, submenu_id: int, db: Session):
        query = await db.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "select"))
        submenu = query.scalars().first()

        if submenu:
            key = [
                f"menu_{menu_id}",
                "menus_list",
                f"submenu_{menu_id}",
                f"submenu_{menu_id}_{submenu.id}",
                f"dish_{menu_id}_{submenu.id}",
            ]
            await cache.delete_one(key)

            await db.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "delete"))
            await db.commit()

            return {
                "status": "true",
                "message": "The submenu has been deleted",
            }
        else:
            ServiceExc.not_found_404("submenu")


class DishCrud:
    """Requests by dish"""

    async def get_list(self, menu_id: int, submenu_id: int, db: Session):
        key = f"dish_{menu_id}_{submenu_id}"
        cache_dishes = await cache.get(key)

        if cache_dishes:
            return cache_dishes

        query = await db.execute(ServiceQuery.select_dish_list(menu_id, submenu_id))
        dishes = query.scalars().all()

        if dishes:
            await cache.set(key, dishes)

        return dishes

    async def get_id_dish(self, menu_id: int, submenu_id: int, dish_id: int, db: Session):
        key = f"dish_{menu_id}_{submenu_id}_{dish_id}"
        cache_dish = await cache.get(key)

        if cache_dish:
            return cache_dish

        query = await db.execute(ServiceQuery.select_dish(menu_id, submenu_id, dish_id))
        dish = query.scalars().first()

        if not dish:
            ServiceExc.not_found_404("dish")

        await cache.set(key, dish)
        return dish

    async def create(self, menu_id: int, submenu_id: int, dish_data: DishCreate, db: Session):
        try:
            key = [
                f"menu_{menu_id}",
                "menus_list",
                f"submenu_{menu_id}",
                f"dish_{menu_id}_{submenu_id}",
            ]
            await cache.delete_all(key)

            query_submenu = await db.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "select"))
            submenu = query_submenu.scalars().first()

            if not submenu:
                ServiceExc.not_found_404("submenu")

            dish_db = Dish(submenu_id=submenu_id, **dict(dish_data))  # type: ignore[call-arg]
            db.add(dish_db)
            await db.commit()
            await db.refresh(dish_db)
            return dish_db
        except IntegrityError:
            ServiceExc.unique_violation("Dish")

    async def update(self, menu_id: int, submenu_id: int, dish_id: int, dish_data: DishUpdate, db: Session):
        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{submenu_id}",
            f"dish_{menu_id}_{submenu_id}",
            f"dish_{menu_id}_{submenu_id}_{dish_id}",
        ]
        await cache.delete_one(key)

        try:
            query = await db.execute(ServiceQuery.select_or_del_dish(menu_id, submenu_id, dish_id, "select"))
            dish = query.scalars().first()

            dish.title = dish_data.title if dish_data.title else dish.title
            dish.description = dish_data.description if dish_data.description else dish.description
            dish.price = dish_data.price if dish_data.price else dish.price
            db.add(dish)
            await db.commit()
            await db.refresh(dish)
            return dish
        except IntegrityError:
            ServiceExc.unique_violation("Dish")
        except AttributeError:
            ServiceExc.not_found_404("dish")

    async def delete(self, menu_id: int, submenu_id: int, dish_id: int, db: Session):
        try:
            query = await db.execute(ServiceQuery.select_or_del_dish(menu_id, submenu_id, dish_id, "select"))
            dish = query.scalars().first()

            key = [
                f"menu_{menu_id}",
                "menus_list",
                f"submenu_{menu_id}",
                f"submenu_{menu_id}_{submenu_id}",
                f"dish_{menu_id}_{submenu_id}",
                f"dish_{menu_id}_{submenu_id}_{dish.id}",
            ]
            await cache.delete_one(key)

            await db.execute(ServiceQuery.select_or_del_dish(menu_id, submenu_id, dish_id, "delete"))
            await db.commit()

            return {
                "status": "true",
                "message": "The dish has been deleted",
            }
        except AttributeError:
            ServiceExc.not_found_404("dish")


class TestMenu:
    @staticmethod
    async def create_test_menu(db: Session):
        with open("./generate_data.json") as file:
            menus = json.load(file)

        for menu in menus:
            menu_create = await ServiceQuery.add_test_data(
                title=menu["title"], desc=menu["description"], table="menu", db=db
            )
            for submenu in menu["submenus"]:
                submenu_create = await ServiceQuery.add_test_data(
                    title=submenu["title"], desc=submenu["description"], table="submenu", db=db, id=menu_create.id
                )
                for dish in submenu["dishes"]:
                    await ServiceQuery.add_test_data(
                        title=dish["title"],
                        desc=dish["description"],
                        price=dish["price"],
                        table="dish",
                        db=db,
                        id=submenu_create.id,
                    )

        return {"Message": "The database is full"}


menu = MenuCrud()
submenu = SubmenuCrud()
dish = DishCrud()
