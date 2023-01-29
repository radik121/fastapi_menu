from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.engine import get_session
from db import models
from schemas.menu import MenuCreate, Menu, MenuUpdate
from schemas.submenu import Submenu, SubmenuCreate, SubmenuUpdate
from schemas.dish import Dish, DishCreate, DishUpdate
from .operations import menu, submenu, dish


router = APIRouter(
    prefix='/api/v1'
    )


###Menu###

@router.get(
    '/menus',
    response_model=List[Menu],
    tags=['menu']
    )
def get_menu_list(db: Session = Depends(get_session)) -> List[models.Menu]:
    return menu.get_list(db)


@router.get(
    '/menus/{menu_id}',
    response_model=Menu,
    tags=['menu']
    )
def get_menu(menu_id: int, db: Session = Depends(get_session)) -> models.Menu:
    return menu.get_id_menu(menu_id, db)  
    

@router.post(
    '/menus',
    response_model=Menu,
    status_code=status.HTTP_201_CREATED,
    tags=['menu']
    )
def create_menu(menu_data: MenuCreate, db: Session = Depends(get_session)) -> Menu:
    return menu.create(menu_data, db)


@router.patch(
    '/menus/{menu_id}',
    response_model=Menu,
    tags=['menu']
    )
def update_menu(menu_id: int, menu_data: MenuUpdate, db: Session = Depends(get_session)) -> Menu:
    return menu.update(menu_id, menu_data, db)


@router.delete(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    tags=['menu']
    )
def delete_menu(menu_id: int, db: Session = Depends(get_session)):
    return menu.delete(menu_id, db)


###Submenu###

@router.get(
    '/menus/{menu_id}/submenus',
    response_model=List[Submenu],
    tags=['submenu'])
def get_submenu_list(menu_id: int, db: Session = Depends(get_session)) -> List[models.Submenu]:
    return submenu.get_list(menu_id, db)


@router.get(
    '/menus/{menu_id}/submenus/{submenu_id}',
    response_model=Submenu,
    tags=['submenu']
    )
def get_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_session)) -> models.Submenu:
    return submenu.get_id_submenu(menu_id, submenu_id, db)


@router.post(
    '/menus/{menu_id}/submenus',
    response_model=Submenu,
    status_code=status.HTTP_201_CREATED,
    tags=['submenu']
    )
def create_submenu(menu_id: int, submenu_data: SubmenuCreate, db: Session = Depends(get_session)) -> Submenu:
    return submenu.create(menu_id, submenu_data, db)


@router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}',
    response_model=Submenu,
    tags=['submenu']
    )
def update_submenu(menu_id: int, submenu_id: int,submenu_data: SubmenuUpdate, db: Session = Depends(get_session)) -> Submenu:
    return submenu.update(menu_id, submenu_id, submenu_data, db)
    

@router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}',
    status_code=status.HTTP_200_OK,
    tags=['submenu']
    )
def delete_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_session)):
    return submenu.delete(menu_id, submenu_id, db)


###Dish###

@router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=List[Dish],
    tags=['dish']
    )
def get_dish_list(menu_id: int, submenu_id: int, db: Session = Depends(get_session)) -> List[models.Dish]:
    return dish.get_list(menu_id, submenu_id, db)


@router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=Dish,
    tags=['dish']
    )
def get_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_session)) -> models.Dish:
    return dish.get_id_dish(menu_id, submenu_id, dish_id, db)


@router.post(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=Dish, status_code=status.HTTP_201_CREATED,
    tags=['dish']
    )
def create_dish(menu_id: int, submenu_id: int, dish_data: DishCreate, db: Session = Depends(get_session)) -> Dish:
    return dish.create(menu_id, submenu_id, dish_data, db)


@router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=Dish,
    tags=['dish']
    )
def update_dish(menu_id: int, submenu_id: int, dish_id: int, dish_data: DishUpdate, db: Session = Depends(get_session)) -> Dish:
    return dish.update(menu_id, submenu_id, dish_id, dish_data, db)


@router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    tags=['dish']
    )
def delete_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_session)):
    return dish.delete(menu_id, submenu_id, dish_id, db)