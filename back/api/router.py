from db import models
from db.redis import redis_client
from fastapi import APIRouter, Depends, status
from schemas.dish import Dish, DishCreate, DishDelete, DishUpdate
from schemas.menu import Menu, MenuCreate, MenuDelete, MenuUpdate
from schemas.submenu import Submenu, SubmenuCreate, SubmenuDelete, SubmenuUpdate

from .operations import DishCrud, MenuCrud, SubmenuCrud, TaskMenu, TestMenu

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
async def get_menu_list(menu: MenuCrud = Depends()) -> list[models.Menu]:
    return await menu.get_list()


@router.get(
    "/menus/{menu_id}",
    response_model=Menu,
    tags=["menu"],
    summary="Конкретное меню",
)
async def get_menu(menu_id: int, menu: MenuCrud = Depends()) -> models.Menu:
    return await menu.get_id_menu(menu_id)


@router.post(
    "/menus",
    response_model=Menu,
    status_code=status.HTTP_201_CREATED,
    tags=["menu"],
    summary="Создание меню",
)
async def create_menu(menu_data: MenuCreate, menu: MenuCrud = Depends()) -> Menu:
    return await menu.create(menu_data)


@router.patch(
    "/menus/{menu_id}",
    response_model=Menu,
    tags=["menu"],
    summary="Изменение конкрентного меню",
)
async def update_menu(menu_id: int, menu_data: MenuUpdate, menu: MenuCrud = Depends()) -> Menu:
    return await menu.update(menu_id, menu_data)


@router.delete(
    "/menus/{menu_id}",
    status_code=status.HTTP_200_OK,
    response_model=MenuDelete,
    tags=["menu"],
    summary="Удаление конкрентного меню",
)
async def delete_menu(menu_id: int, menu: MenuCrud = Depends()):
    return await menu.delete(menu_id)


@router.get(
    "/menus/{menu_id}/submenus",
    response_model=list[Submenu],
    tags=["submenu"],
    summary="Список подменю",
)
async def get_submenu_list(menu_id: int, submenu: SubmenuCrud = Depends()) -> list[models.Submenu]:
    return await submenu.get_list(menu_id)


@router.get(
    "/menus/{menu_id}/submenus/{submenu_id}",
    response_model=Submenu,
    tags=["submenu"],
    summary="Конкрентное подменю",
)
async def get_submenu(menu_id: int, submenu_id: int, submenu: SubmenuCrud = Depends()) -> models.Submenu:
    return await submenu.get_id_submenu(menu_id, submenu_id)


@router.post(
    "/menus/{menu_id}/submenus",
    response_model=Submenu,
    status_code=status.HTTP_201_CREATED,
    tags=["submenu"],
    summary="Создание подменю",
)
async def create_submenu(menu_id: int, submenu_data: SubmenuCreate, submenu: SubmenuCrud = Depends()) -> Submenu:
    return await submenu.create(menu_id, submenu_data)


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
    submenu: SubmenuCrud = Depends(),
) -> Submenu:
    return await submenu.update(menu_id, submenu_id, submenu_data)


@router.delete(
    "/menus/{menu_id}/submenus/{submenu_id}",
    status_code=status.HTTP_200_OK,
    response_model=SubmenuDelete,
    tags=["submenu"],
    summary="Удаление конкрентного подменю",
)
async def delete_submenu(menu_id: int, submenu_id: int, submenu: SubmenuCrud = Depends()):
    return await submenu.delete(menu_id, submenu_id)


@router.get(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=list[Dish],
    tags=["dish"],
    summary="Список блюд",
)
async def get_dish_list(menu_id: int, submenu_id: int, dish: DishCrud = Depends()) -> list[models.Dish]:
    return await dish.get_list(menu_id, submenu_id)


@router.get(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=Dish,
    tags=["dish"],
    summary="Конкрентное блюдо",
)
async def get_dish(menu_id: int, submenu_id: int, dish_id: int, dish: DishCrud = Depends()) -> models.Dish:
    return await dish.get_id_dish(menu_id, submenu_id, dish_id)


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
    dish: DishCrud = Depends(),
) -> Dish:
    return await dish.create(menu_id, submenu_id, dish_data)


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
    dish: DishCrud = Depends(),
) -> Dish:
    return await dish.update(menu_id, submenu_id, dish_id, dish_data)


@router.delete(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    status_code=status.HTTP_200_OK,
    response_model=DishDelete,
    tags=["dish"],
    summary="Удаление конкрентного блюда",
)
async def delete_dish(menu_id: int, submenu_id: int, dish_id: int, dish: DishCrud = Depends()):
    return await dish.delete(menu_id, submenu_id, dish_id)


@router.get(
    "/generate_data",
    status_code=status.HTTP_200_OK,
    tags=["test_data"],
    summary="Автогенерация тестовых данных в БД",
)
async def generate_data_db(test_menu: TestMenu = Depends()):
    return await test_menu.create_test_menu()


@router.post(
    path="/task_file",
    status_code=status.HTTP_201_CREATED,
    tags=["download_menu"],
    summary="Создание задачи на получения меню",
)
async def create_task_full_menu(task_worker: TaskMenu = Depends()):
    return await task_worker.all_data_to_file()


@router.get(
    path="/task_file/{task_id}",
    status_code=status.HTTP_200_OK,
    tags=["download_menu"],
    summary="Получение ссылки на файла",
)
async def get_download_file(task_id: str, task_worker: TaskMenu = Depends()):
    return task_worker.get_data_to_file(task_id)
