from db.models import Dish, Menu, Submenu
from fastapi import HTTPException, Query, status
from sqlalchemy import delete, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class ServiceExc:
    @staticmethod
    def not_found_404(value: str) -> HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{value} not found",
        )

    @staticmethod
    def unique_violation(value: str) -> HTTPException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{value} title already exists",
        )


class ServiceQuery:
    @staticmethod
    def select_or_delete_menu(menu_id: int, method: str) -> Query:
        match method:
            case "select":
                query = select(Menu).filter(Menu.id == menu_id)
            case "delete":
                query = delete(Menu).filter(Menu.id == menu_id)
        return query

    @staticmethod
    def select_menu_list() -> Query:
        """Select all menu"""
        query = (
            select(
                Menu,
                func.count(distinct(Submenu.id)),
                func.count(Dish.id),
            )
            .join(
                Menu.submenus,
                isouter=True,
            )
            .join(
                Submenu.dishes,
                isouter=True,
            )
            .group_by(
                Menu.id,
            )
        )
        return query

    @staticmethod
    def select_menu(menu_id: int) -> Query:
        """Select one menu"""
        query = (
            select(
                Menu,
                func.count(distinct(Submenu.id)),
                func.count(Dish.id),
            )
            .join(
                Menu.submenus,
                isouter=True,
            )
            .join(
                Submenu.dishes,
                isouter=True,
            )
            .filter(Menu.id == menu_id)
            .group_by(Menu.id)
        )
        return query

    @staticmethod
    def select_submenu_list(menu_id: int) -> Query:
        query = (
            select(
                Submenu,
                func.count(Dish.id),
            )
            .join(
                Submenu.dishes,
                isouter=True,
            )
            .filter(
                Submenu.menu_id == menu_id,
            )
            .group_by(Submenu.id)
        )
        return query

    @staticmethod
    def select_submenu(menu_id: int, submenu_id: int) -> Query:
        query = (
            select(
                Submenu,
                func.count(Dish.id),
            )
            .join(
                Submenu.dishes,
                isouter=True,
            )
            .filter(
                Submenu.menu_id == menu_id,
            )
            .filter(
                Submenu.id == submenu_id,
            )
            .group_by(
                Submenu.id,
            )
        )
        return query

    @staticmethod
    def select_or_del_submenu(menu_id: int, submenu_id: int, method: str) -> Query:
        match method:
            case "select":
                query = (
                    select(
                        Submenu,
                    )
                    .filter(
                        Submenu.id == submenu_id,
                    )
                    .filter(
                        Submenu.menu_id == menu_id,
                    )
                )
            case "delete":
                query = (
                    delete(
                        Submenu,
                    )
                    .filter(
                        Submenu.id == submenu_id,
                    )
                    .filter(
                        Submenu.menu_id == menu_id,
                    )
                )
        return query

    @staticmethod
    def select_dish_list(menu_id: int, submenu_id: int) -> Query:
        query = (
            select(
                Dish,
            )
            .join(
                Submenu,
            )
            .filter(
                Submenu.id == submenu_id,
                Submenu.menu_id == menu_id,
            )
        )
        return query

    @staticmethod
    def select_dish(menu_id: int, submenu_id: int, dish_id: int) -> Query:
        query = (
            select(
                Dish,
            )
            .join(
                Submenu,
            )
            .filter(
                Submenu.id == submenu_id,
                Submenu.menu_id == menu_id,
                Dish.id == dish_id,
            )
        )
        return query

    @staticmethod
    def select_or_del_dish(menu_id: int, submenu_id: int, dish_id: int, method: str) -> Query:
        match method:
            case "select":
                query = (
                    select(
                        Dish,
                    )
                    .join(
                        Submenu,
                    )
                    .filter(
                        Submenu.id == submenu_id,
                        Submenu.menu_id == menu_id,
                        Dish.id == dish_id,
                    )
                )
            case "delete":
                query = delete(
                    Dish,
                ).filter(
                    Dish.submenu_id == submenu_id,
                    Dish.id == dish_id,
                )
        return query

    @staticmethod
    async def add_test_data(
        title: str, desc: str, table: str, db: AsyncSession, id: int | None = None, price: str | None = None
    ) -> Query:
        match table:
            case "menu":
                data = Menu(title=title, description=desc)  # type: ignore[call-arg, assignment]
            case "submenu":
                data = Submenu(title=title, description=desc, menu_id=id)  # type: ignore[call-arg, assignment]
            case "dish":
                data = Dish(
                    title=title, description=desc, price=price, submenu_id=id
                )  # type: ignore[call-arg, assignment]

        db.add(data)
        await db.commit()
        await db.refresh(data)
        return data

    @staticmethod
    def get_all_menu():
        query = select(Menu).options(joinedload(Menu.submenus).joinedload(Submenu.dishes))

        return query
