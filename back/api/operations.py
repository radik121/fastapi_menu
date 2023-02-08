import json

from api.tasks import get_result, save_data_to_xlsx
from db.engine import get_session
from db.models import Dish, Menu, Submenu
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from schemas.dish import DishCreate, DishUpdate
from schemas.menu import MenuCreate, MenuUpdate
from schemas.submenu import SubmenuCreate, SubmenuUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .cache import cache
from .service import ServiceExc, ServiceQuery


class GetSession:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session


class MenuCrud(GetSession):
    """Requests by menu"""

    async def get_list(self):
        key = "menus_list"
        cache_menus = await cache.get(key)

        if cache_menus:
            return cache_menus

        query = await self.session.execute(ServiceQuery.select_menu_list())
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

    async def get_id_menu(self, menu_id: int):
        key = f"menu_{menu_id}"
        cache_menu = await cache.get(key)

        if cache_menu:
            return cache_menu

        query = await self.session.execute(ServiceQuery.select_menu(menu_id))
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

    async def create(self, menu_data: MenuCreate):
        try:
            await cache.delete_one(["menus_list"])
            menu_db = Menu(**menu_data.dict())
            self.session.add(menu_db)
            await self.session.commit()
            await self.session.refresh(menu_db)
            return menu_db
        except IntegrityError:
            ServiceExc.unique_violation("Menu")

    async def update(self, menu_id: int, menu_data: MenuUpdate):
        key = [f"menu_{menu_id}", "menus_list"]

        query = await self.session.execute(ServiceQuery.select_menu(menu_id))
        result = query.first()

        if result:
            menu = result[0]
            menu.submenus_count = result[1]
            menu.dishes_count = result[2]
            menu.title = menu_data.title if menu_data.title else menu.title
            menu.description = menu_data.description if menu_data.description else menu.description
            self.session.add(menu)
            await self.session.commit()
            await self.session.refresh(menu)

            await cache.delete_one(key)
            return menu
        else:
            ServiceExc.not_found_404("menu")

    async def delete(self, menu_id: int):
        query = await self.session.execute(ServiceQuery.select_or_delete_menu(menu_id, "select"))
        result = query.first()

        if not result:
            ServiceExc.not_found_404("menu")

        await self.session.execute(ServiceQuery.select_or_delete_menu(menu_id, "delete"))
        await self.session.commit()

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


class SubmenuCrud(GetSession):
    """Requests by submenu"""

    async def get_list(self, menu_id: int):
        key = f"submenu_{menu_id}"
        cache_submenus = await cache.get(key)

        if cache_submenus:
            return cache_submenus

        query = await self.session.execute(ServiceQuery.select_submenu_list(menu_id))
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

    async def get_id_submenu(self, menu_id: int, submenu_id: int):
        key = f"submenu_{menu_id}_{submenu_id}"
        cache_submenu = await cache.get(key)

        if cache_submenu:
            return cache_submenu

        query = await self.session.execute(ServiceQuery.select_submenu(menu_id, submenu_id))
        result = query.first()

        if not result:
            ServiceExc.not_found_404("submenu")

        submenu = result[0]
        submenu.dishes_count = result[1]

        if submenu:
            await cache.set(key, submenu)

        return submenu

    async def create(self, menu_id: int, submenu_data: SubmenuCreate):
        try:
            key = [f"menu_{menu_id}", "menus_list", f"submenu_{menu_id}"]
            await cache.delete_one(key)

            result = await self.session.execute(ServiceQuery.select_or_delete_menu(menu_id, "select"))
            menu = result.first()

            if not menu:
                ServiceExc.not_found_404("menu")

            submenu_db = Submenu(menu_id=menu_id, **dict(submenu_data))  # type: ignore[call-arg]
            self.session.add(submenu_db)
            await self.session.commit()
            await self.session.refresh(submenu_db)
            return submenu_db
        except IntegrityError:
            ServiceExc.unique_violation("Submenu")

    async def update(self, menu_id: int, submenu_id: int, submenu_data: SubmenuUpdate):
        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{submenu_id}",
        ]
        await cache.delete_one(key)

        query = await self.session.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "select"))
        submenu = query.scalars().first()

        if submenu:
            submenu.title = submenu_data.title if submenu_data.title else submenu.title
            submenu.description = submenu_data.description if submenu_data.description else submenu.description
            self.session.add(submenu)
            await self.session.commit()
            await self.session.refresh(submenu)
            return submenu
        else:
            ServiceExc.not_found_404("submenu")

    async def delete(self, menu_id: int, submenu_id: int):
        query = await self.session.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "select"))
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

            await self.session.execute(ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "delete"))
            await self.session.commit()

            return {
                "status": "true",
                "message": "The submenu has been deleted",
            }
        else:
            ServiceExc.not_found_404("submenu")


class DishCrud(GetSession):
    """Requests by dish"""

    async def get_list(self, menu_id: int, submenu_id: int):
        key = f"dish_{menu_id}_{submenu_id}"
        cache_dishes = await cache.get(key)

        if cache_dishes:
            return cache_dishes

        query = await self.session.execute(ServiceQuery.select_dish_list(menu_id, submenu_id))
        dishes = query.scalars().all()

        if dishes:
            await cache.set(key, dishes)

        return dishes

    async def get_id_dish(self, menu_id: int, submenu_id: int, dish_id: int):
        key = f"dish_{menu_id}_{submenu_id}_{dish_id}"
        cache_dish = await cache.get(key)

        if cache_dish:
            return cache_dish

        query = await self.session.execute(ServiceQuery.select_dish(menu_id, submenu_id, dish_id))
        dish = query.scalars().first()

        if not dish:
            ServiceExc.not_found_404("dish")

        await cache.set(key, dish)
        return dish

    async def create(self, menu_id: int, submenu_id: int, dish_data: DishCreate):
        try:
            key = [
                f"menu_{menu_id}",
                "menus_list",
                f"submenu_{menu_id}",
                f"dish_{menu_id}_{submenu_id}",
            ]
            await cache.delete_all(key)

            query_submenu = await self.session.execute(
                ServiceQuery.select_or_del_submenu(menu_id, submenu_id, "select")
            )
            submenu = query_submenu.scalars().first()

            if not submenu:
                ServiceExc.not_found_404("submenu")

            dish_db = Dish(submenu_id=submenu_id, **dict(dish_data))  # type: ignore[call-arg]
            self.session.add(dish_db)
            await self.session.commit()
            await self.session.refresh(dish_db)
            return dish_db
        except IntegrityError:
            ServiceExc.unique_violation("Dish")

    async def update(self, menu_id: int, submenu_id: int, dish_id: int, dish_data: DishUpdate):
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
            query = await self.session.execute(ServiceQuery.select_or_del_dish(menu_id, submenu_id, dish_id, "select"))
            dish = query.scalars().first()

            dish.title = dish_data.title if dish_data.title else dish.title
            dish.description = dish_data.description if dish_data.description else dish.description
            dish.price = dish_data.price if dish_data.price else dish.price
            self.session.add(dish)
            await self.session.commit()
            await self.session.refresh(dish)
            return dish
        except IntegrityError:
            ServiceExc.unique_violation("Dish")
        except AttributeError:
            ServiceExc.not_found_404("dish")

    async def delete(self, menu_id: int, submenu_id: int, dish_id: int):
        try:
            query = await self.session.execute(ServiceQuery.select_or_del_dish(menu_id, submenu_id, dish_id, "select"))
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

            await self.session.execute(ServiceQuery.select_or_del_dish(menu_id, submenu_id, dish_id, "delete"))
            await self.session.commit()

            return {
                "status": "true",
                "message": "The dish has been deleted",
            }
        except AttributeError:
            ServiceExc.not_found_404("dish")


class TestMenu(GetSession):
    """Generate test data finto DB"""

    async def create_test_menu(self):
        with open("./generate_data.json") as file:
            menus = json.load(file)

        for menu in menus:
            menu_create = await ServiceQuery.add_test_data(
                title=menu["title"],
                desc=menu["description"],
                table="menu",
                db=self.session,
            )
            for submenu in menu["submenus"]:
                submenu_create = await ServiceQuery.add_test_data(
                    title=submenu["title"],
                    desc=submenu["description"],
                    table="submenu",
                    db=self.session,
                    id=menu_create.id,
                )
                for dish in submenu["dishes"]:
                    await ServiceQuery.add_test_data(
                        title=dish["title"],
                        desc=dish["description"],
                        price=dish["price"],
                        table="dish",
                        db=self.session,
                        id=submenu_create.id,
                    )

        return {"Message": "The database is full"}


class AllMenu(GetSession):
    """Request all menu from db"""

    async def all_menu(self):
        query_result = await self.session.execute(ServiceQuery.get_all_menu())
        result = jsonable_encoder(query_result.scalars().unique().all())

        return result


class TaskMenu(AllMenu):
    async def all_data_to_file(self):
        data = await self.all_menu()
        task = save_data_to_xlsx.delay(data)
        return {"status": "True", "task id": {task.id}}

    def get_data_to_file(self, task_id: str):
        task = get_result(task_id)
        if task.ready():
            filename = task.result["file_name"]
            return FileResponse(
                path=f"/app/task_files/{filename}",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
        else:
            return {"task_id": task_id, "status": task.status}
