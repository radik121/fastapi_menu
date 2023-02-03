from db import models
from fastapi import HTTPException, status
from psycopg2.errors import UniqueViolation
from schemas.dish import DishCreate, DishUpdate
from schemas.menu import MenuCreate, MenuUpdate
from schemas.submenu import SubmenuCreate, SubmenuUpdate
from sqlalchemy import distinct, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .cache import cache


def not_found_404(value: str) -> HTTPException:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{value} not found",
    )


def unique_violation(value: str) -> HTTPException:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{value} title already exists",
    )


class MenuCrud:
    """Requests by menu"""

    def get_list(self, db: Session):
        key = "menus_list"
        cache_menus = cache.get(key)

        if cache_menus:
            return cache_menus

        query = (
            db.query(
                models.Menu,
                func.count(distinct(models.Menu.submenus)),
                func.count(models.Submenu.dishes),
            )
            .join(
                models.Menu.submenus,
                isouter=True,
            )
            .join(
                models.Submenu.dishes,
                isouter=True,
            )
            .group_by(models.Menu.id)
            .all()
        )

        menus = []
        for i in query:
            item = None
            item = i[0]
            item.submenus_count = i[1]
            item.dishes_count = i[2]
            menus.append(item)

        if menus:
            cache.set(key, menus)

        return menus

    def get_id_menu(self, menu_id: int, db: Session):
        key = f"menu_{menu_id}"
        cache_menu = cache.get(key)

        if cache_menu:
            return cache_menu

        query = (
            db.query(
                models.Menu,
                func.count(distinct(models.Menu.submenus)),
                func.count(models.Submenu.dishes),
            )
            .join(
                models.Menu.submenus,
                isouter=True,
            )
            .join(
                models.Submenu.dishes,
                isouter=True,
            )
            .filter(
                models.Menu.id == menu_id,
            )
            .group_by(
                models.Menu.id,
            )
            .first()
        )

        if not query:
            not_found_404("menu")

        menu = query[0]
        menu.submenus_count = query[1]
        menu.dishes_count = query[2]

        if menu:
            cache.set(key, menu)

        return menu

    def create(self, menu_data: MenuCreate, db: Session):
        try:
            cache.delete_one(["menus_list"])
            menu_db = models.Menu(**menu_data.dict())
            db.add(menu_db)
            db.commit()
            db.refresh(menu_db)
            return menu_db
        except IntegrityError as error:
            if isinstance(error.orig, UniqueViolation):
                unique_violation("Menu")

    def update(self, menu_id: int, menu_data: MenuUpdate, db: Session):
        key = [f"menu_{menu_id}", "menus_list"]

        query = (
            db.query(
                models.Menu,
                func.count(distinct(models.Menu.submenus)),
                func.count(models.Submenu.dishes),
            )
            .join(
                models.Menu.submenus,
                isouter=True,
            )
            .join(
                models.Submenu.dishes,
                isouter=True,
            )
            .filter(models.Menu.id == menu_id)
            .group_by(models.Menu.id)
            .first()
        )

        if not query:
            not_found_404("menu")

        menu = query[0]
        menu.submenus_count = query[1]
        menu.dishes_count = query[2]
        menu.title = menu_data.title if menu_data.title else menu.title
        menu.description = menu_data.description if menu_data.description else menu.description
        db.add(menu)
        db.commit()
        db.refresh(menu)

        cache.delete_one(key)
        return menu

    def delete(self, menu_id: int, db: Session):
        query = (
            db.query(
                models.Menu,
            )
            .filter(
                models.Menu.id == menu_id,
            )
            .first()
        )

        if not query:
            not_found_404("menu")

        db.delete(query)
        db.commit()

        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"dish_{menu_id}",
        ]
        cache.delete_all(key)

        return {
            "status": "true",
            "message": "The menu has been deleted",
        }


class SubmenuCrud:
    """Requests by submenu"""

    def get_list(self, menu_id: int, db: Session):
        key = f"submenu_{menu_id}"
        cache_submenus = cache.get(key)

        if cache_submenus:
            return cache_submenus

        query = (
            db.query(
                models.Submenu,
                func.count(models.Submenu.dishes),
            )
            .join(
                models.Submenu.dishes,
                isouter=True,
            )
            .filter(
                models.Submenu.menu_id == menu_id,
            )
            .group_by(models.Submenu.id)
            .all()
        )

        submenus = []
        for i in query:
            item = None
            item = i[0]
            item.dishes_count = i[1]
            submenus.append(item)

        if submenus:
            cache.set(key, submenus)

        return submenus

    def get_id_submenu(self, menu_id: int, submenu_id: int, db: Session):
        key = f"submenu_{menu_id}_{submenu_id}"
        cache_submenu = cache.get(key)

        if cache_submenu:
            return cache_submenu

        query = (
            db.query(
                models.Submenu,
                func.count(models.Submenu.dishes),
            )
            .join(
                models.Submenu.dishes,
                isouter=True,
            )
            .filter(
                models.Submenu.menu_id == menu_id,
            )
            .filter(
                models.Submenu.id == submenu_id,
            )
            .group_by(
                models.Submenu.id,
            )
            .first()
        )

        if not query:
            not_found_404("submenu")

        submenu = query[0]
        submenu.dishes_count = query[1]

        if submenu:
            cache.set(key, submenu)

        return submenu

    def create(self, menu_id: int, submenu_data: SubmenuCreate, db: Session):
        try:
            key = [f"menu_{menu_id}", "menus_list", f"submenu_{menu_id}"]
            cache.delete_one(key)

            menu = (
                db.query(
                    models.Menu,
                )
                .filter(
                    models.Menu.id == menu_id,
                )
                .first()
            )

            if not menu:
                not_found_404("menu")

            submenu_db = models.Submenu(**submenu_data.dict())
            menu.submenus.append(submenu_db)
            db.commit()
            db.refresh(submenu_db)
            return submenu_db
        except IntegrityError as error:
            if isinstance(error.orig, UniqueViolation):
                unique_violation("Submenu")

    def update(self, menu_id: int, submenu_id: int, submenu_data: SubmenuUpdate, db: Session):
        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{submenu_id}",
        ]
        cache.delete_one(key)

        submenu = (
            db.query(
                models.Submenu,
            )
            .filter(
                models.Submenu.id == submenu_id,
            )
            .filter(
                models.Submenu.menu_id == menu_id,
            )
            .first()
        )

        if not submenu:
            not_found_404("submenu")

        submenu.title = submenu_data.title if submenu_data.title else submenu.title
        submenu.description = submenu_data.description if submenu_data.description else submenu.description
        db.add(submenu)
        db.commit()
        db.refresh(submenu)

        return submenu

    def delete(self, menu_id: int, submenu_id: int, db: Session):
        query = (
            db.query(
                models.Submenu,
            )
            .filter(
                models.Submenu.id == submenu_id,
            )
            .filter(
                models.Submenu.menu_id == menu_id,
            )
            .first()
        )

        if not query:
            not_found_404("submenu")

        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{query.id}",
            f"dish_{menu_id}_{query.id}",
        ]
        cache.delete_one(key)

        db.delete(query)
        db.commit()

        return {
            "status": "true",
            "message": "The submenu has been deleted",
        }


class DishCrud:
    """Requests by dish"""

    def get_list(self, menu_id: int, submenu_id: int, db: Session):
        key = f"dish_{menu_id}_{submenu_id}"
        cache_dishes = cache.get(key)

        if cache_dishes:
            return cache_dishes

        dishes = (
            db.query(
                models.Dish,
            )
            .join(
                models.Submenu,
            )
            .filter(
                models.Submenu.id == submenu_id,
                models.Submenu.menu_id == menu_id,
            )
            .all()
        )

        if dishes:
            cache.set(key, dishes)

        return dishes

    def get_id_dish(self, menu_id: int, submenu_id: int, dish_id: int, db: Session):
        key = f"dish_{menu_id}_{submenu_id}_{dish_id}"
        cache_dish = cache.get(key)

        if cache_dish:
            return cache_dish

        dish = (
            db.query(
                models.Dish,
            )
            .join(
                models.Submenu,
            )
            .filter(
                models.Submenu.id == submenu_id,
                models.Submenu.menu_id == menu_id,
                models.Dish.id == dish_id,
            )
            .first()
        )

        if not dish:
            not_found_404("dish")

        cache.set(key, dish)
        return dish

    def create(self, menu_id: int, submenu_id: int, dish_data: DishCreate, db: Session):
        try:
            key = [
                f"menu_{menu_id}",
                "menus_list",
                f"submenu_{menu_id}",
                f"submenu_{menu_id}_{submenu_id}",
                f"dish_{menu_id}_{submenu_id}",
            ]
            cache.delete_one(key)

            submenu = (
                db.query(
                    models.Submenu,
                )
                .filter(
                    models.Submenu.id == submenu_id,
                    models.Submenu.menu_id == menu_id,
                )
                .first()
            )

            if not submenu:
                not_found_404("submenu")

            dish_db = models.Dish(**dict(dish_data))
            submenu.dishes.append(dish_db)
            db.commit()
            db.refresh(dish_db)
            return dish_db
        except IntegrityError as error:
            if isinstance(error.orig, UniqueViolation):
                unique_violation("Dish")

    def update(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int,
        dish_data: DishUpdate,
        db: Session,
    ):
        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{submenu_id}",
            f"dish_{menu_id}_{submenu_id}",
            f"dish_{menu_id}_{submenu_id}_{dish_id}",
        ]
        cache.delete_one(key)

        dish = (
            db.query(
                models.Dish,
            )
            .join(
                models.Submenu,
            )
            .filter(
                models.Submenu.id == submenu_id,
                models.Submenu.menu_id == menu_id,
                models.Dish.id == dish_id,
            )
            .first()
        )

        if not dish:
            not_found_404("dish")

        dish.title = dish_data.title if dish_data.title else dish.title
        dish.description = dish_data.description if dish_data.description else dish.description
        dish.price = dish_data.price if dish_data.price else dish.price
        db.add(dish)
        db.commit()
        db.refresh(dish)

        return dish

    def delete(self, menu_id: int, submenu_id: int, dish_id: int, db: Session):
        dish = (
            db.query(
                models.Dish,
            )
            .join(
                models.Submenu,
            )
            .filter(
                models.Submenu.id == submenu_id,
                models.Submenu.menu_id == menu_id,
                models.Dish.id == dish_id,
            )
            .first()
        )

        if not dish:
            not_found_404("dish")

        key = [
            f"menu_{menu_id}",
            "menus_list",
            f"submenu_{menu_id}",
            f"submenu_{menu_id}_{submenu_id}",
            f"dish_{menu_id}_{submenu_id}",
            f"dish_{menu_id}_{submenu_id}_{dish.id}",
        ]
        cache.delete_one(key)

        db.delete(dish)
        db.commit()

        return {
            "status": "true",
            "message": "The dish has been deleted",
        }


menu = MenuCrud()
submenu = SubmenuCrud()
dish = DishCrud()
