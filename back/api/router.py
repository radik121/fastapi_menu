from db import models
from db.engine import get_session
from db.redis import redis_client
from fastapi import APIRouter, Depends, status
from schemas.dish import Dish, DishCreate, DishDelete, DishUpdate
from schemas.menu import Menu, MenuCreate, MenuDelete, MenuUpdate
from schemas.submenu import Submenu, SubmenuCreate, SubmenuDelete, SubmenuUpdate
from sqlalchemy.orm import Session

from .operations import TestMenu, dish, menu, submenu

router = APIRouter(
    prefix="/api/v1",
)


@router.on_event("startup")
async def startup():
    redis_client


@router.get(
    "/menus",
    response_model=list[Menu],
    tags=["menu"],
    summary="Список меню",
)
async def get_menu_list(db: Session = Depends(get_session)) -> list[models.Menu]:
    return await menu.get_list(db)


@router.get(
    "/menus/{menu_id}",
    response_model=Menu,
    tags=["menu"],
    summary="Конкретное меню",
)
async def get_menu(menu_id: int, db: Session = Depends(get_session)) -> models.Menu:
    return await menu.get_id_menu(menu_id, db)


@router.post(
    "/menus",
    response_model=Menu,
    status_code=status.HTTP_201_CREATED,
    tags=["menu"],
    summary="Создание меню",
)
async def create_menu(menu_data: MenuCreate, db: Session = Depends(get_session)) -> Menu:
    return await menu.create(menu_data, db)


@router.patch(
    "/menus/{menu_id}",
    response_model=Menu,
    tags=["menu"],
    summary="Изменение конкрентного меню",
)
async def update_menu(menu_id: int, menu_data: MenuUpdate, db: Session = Depends(get_session)) -> Menu:
    return await menu.update(menu_id, menu_data, db)


@router.delete(
    "/menus/{menu_id}",
    status_code=status.HTTP_200_OK,
    response_model=MenuDelete,
    tags=["menu"],
    summary="Удаление конкрентного меню",
)
async def delete_menu(menu_id: int, db: Session = Depends(get_session)):
    return await menu.delete(menu_id, db)


@router.get(
    "/menus/{menu_id}/submenus",
    response_model=list[Submenu],
    tags=["submenu"],
    summary="Список подменю",
)
async def get_submenu_list(menu_id: int, db: Session = Depends(get_session)) -> list[models.Submenu]:
    return await submenu.get_list(menu_id, db)


@router.get(
    "/menus/{menu_id}/submenus/{submenu_id}",
    response_model=Submenu,
    tags=["submenu"],
    summary="Конкрентное подменю",
)
async def get_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_session)) -> models.Submenu:
    return await submenu.get_id_submenu(menu_id, submenu_id, db)


@router.post(
    "/menus/{menu_id}/submenus",
    response_model=Submenu,
    status_code=status.HTTP_201_CREATED,
    tags=["submenu"],
    summary="Создание подменю",
)
async def create_submenu(menu_id: int, submenu_data: SubmenuCreate, db: Session = Depends(get_session)) -> Submenu:
    return await submenu.create(menu_id, submenu_data, db)


@router.patch(
    "/menus/{menu_id}/submenus/{submenu_id}",
    response_model=Submenu,
    tags=["submenu"],
    summary="Изменение конкрентного подменю",
)
async def update_submenu(
    menu_id: int,
    submenu_id: int,
    submenu_data: SubmenuUpdate,
    db: Session = Depends(get_session),
) -> Submenu:
    return await submenu.update(menu_id, submenu_id, submenu_data, db)


@router.delete(
    "/menus/{menu_id}/submenus/{submenu_id}",
    status_code=status.HTTP_200_OK,
    response_model=SubmenuDelete,
    tags=["submenu"],
    summary="Удаление конкрентного подменю",
)
async def delete_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_session)):
    return await submenu.delete(menu_id, submenu_id, db)


@router.get(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=list[Dish],
    tags=["dish"],
    summary="Список блюд",
)
async def get_dish_list(menu_id: int, submenu_id: int, db: Session = Depends(get_session)) -> list[models.Dish]:
    return await dish.get_list(menu_id, submenu_id, db)


@router.get(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=Dish,
    tags=["dish"],
    summary="Конкрентное блюдо",
)
async def get_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_session)) -> models.Dish:
    return await dish.get_id_dish(menu_id, submenu_id, dish_id, db)


@router.post(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=Dish,
    status_code=status.HTTP_201_CREATED,
    tags=["dish"],
    summary="Создание блюда",
)
async def create_dish(
    menu_id: int,
    submenu_id: int,
    dish_data: DishCreate,
    db: Session = Depends(get_session),
) -> Dish:
    return await dish.create(menu_id, submenu_id, dish_data, db)


@router.patch(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=Dish,
    tags=["dish"],
    summary="Изменение конкрентного блюда",
)
async def update_dish(
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_session),
) -> Dish:
    return await dish.update(menu_id, submenu_id, dish_id, dish_data, db)


@router.delete(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    status_code=status.HTTP_200_OK,
    response_model=DishDelete,
    tags=["dish"],
    summary="Удаление конкрентного блюда",
)
async def delete_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_session)):
    return await dish.delete(menu_id, submenu_id, dish_id, db)


@router.get("/generate_data", status_code=status.HTTP_200_OK, tags=["test_data"])
async def generate_data_db(db: Session = Depends(get_session)):
    return await TestMenu.create_test_menu(db)
