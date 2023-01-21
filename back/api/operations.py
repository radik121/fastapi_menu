from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from db.engine import get_session
from schemas.menu import MenuCreate, Menu, MenuUpdate
from schemas.submenu import Submenu, SubmenuCreate, SubmenuUpdate
from schemas.dish import Dish, DishCreate, DishUpdate

from sqlalchemy.orm import Session
from db import models
from sqlalchemy import distinct, func, select


router = APIRouter(
    prefix='/api/v1'
    )


###Menu###

@router.get('/menus', response_model=List[Menu], tags=['menu'])
def get_menu_list(db: Session = Depends(get_session)) -> List[models.Menu]:
    query = db.query(
        models.Menu,
        func.count(distinct(models.Menu.submenus)),     # func.count(distinct(models.Submenu.id)),
        func.count(models.Submenu.dishes)               # func.count(models.Dish.id)
    ).join(        
        models.Menu.submenus,                           # models.Submenu, models.Menu.id == models.Submenu.menu_id,
        isouter=True
    ).join(        
        models.Submenu.dishes,                          # models.Dish, models.Submenu.id == models.Dish.submenu_id,
        isouter=True
    ).group_by(models.Menu.id).all()

    menus = []
    for i in query:
        item = None
        item = i[0]
        item.submenus_count = i[1]
        item.dishes_count = i[2]
        menus.append(item)
    return menus


@router.get('/menus/{menu_id}', response_model=Menu, tags=['menu'])
def get_menu(menu_id: int, db: Session = Depends(get_session)) -> models.Menu:
    query = db.query(
        models.Menu,
        func.count(distinct(models.Menu.submenus)),
        func.count(models.Submenu.dishes)
    ).join(
        models.Menu.submenus,
        isouter=True
    ).join(
        models.Submenu.dishes,
        isouter=True
    ).filter(models.Menu.id == menu_id).group_by(models.Menu.id).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="menu not found")

    menu = query[0]
    menu.submenus_count = query[1]
    menu.dishes_count = query[2]
    
    return menu    
    

@router.post('/menus', response_model=Menu, status_code=status.HTTP_201_CREATED, tags=['menu'])
def create_menu(menu: MenuCreate, db: Session = Depends(get_session)) -> Menu:
    menu_db = models.Menu(**menu.dict())
    db.add(menu_db)
    db.commit()
    db.refresh(menu_db)
    return menu_db


@router.patch('/menus/{menu_id}', response_model=Menu, tags=['menu'])
def update_menu(menu_id: int, menu_data: MenuUpdate, db: Session = Depends(get_session)) -> Menu:
    query = db.query(
        models.Menu,
        func.count(distinct(models.Menu.submenus)),
        func.count(models.Submenu.dishes)
    ).join(
        models.Menu.submenus,
        isouter=True
    ).join(
        models.Submenu.dishes,
        isouter=True
    ).filter(models.Menu.id == menu_id).group_by(models.Menu.id).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="menu not found")

    menu = query[0]
    menu.submenus_count = query[1]
    menu.dishes_count = query[2]
    menu.title = menu_data.title if menu_data.title else menu.title
    menu.description = menu_data.description if menu_data.description else menu.description
    db.add(menu)
    db.commit()
    db.refresh(menu)
    
    return menu


@router.delete('/menus/{menu_id}', status_code=status.HTTP_200_OK, tags=['menu'])
def delete_menu(menu_id: int, db: Session = Depends(get_session)):
    query = db.query(models.Menu).filter(models.Menu.id == menu_id).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="menu not found")
    
    db.delete(query)
    db.commit()

    return {"status": "true", "message": "The menu has been deleted"}


###Submenu###

@router.get('/menus/{menu_id}/submenus', response_model=List[Submenu], tags=['submenu'])
def get_submenu_list(menu_id: int, db: Session = Depends(get_session)) -> List[models.Submenu]:
    query = db.query(
        models.Submenu,
        func.count(models.Submenu.dishes)
    ).join(
        models.Submenu.dishes,
        isouter=True
    ).filter(models.Submenu.menu_id == menu_id
    ).group_by(models.Submenu.id).all()
    
    submenus = []
    for i in query:
        item = None
        item = i[0]
        item.dishes_count = i[1]
        submenus.append(item)
    return submenus


@router.get('/menus/{menu_id}/submenus/{submenu_id}', response_model=Submenu, tags=['submenu'])
def get_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_session)) -> models.Submenu:
    query = db.query(
        models.Submenu,
        func.count(models.Submenu.dishes)
    ).join(
        models.Submenu.dishes,
        isouter=True
    ).filter(models.Submenu.menu_id == menu_id
    ).filter(models.Submenu.id == submenu_id
    ).group_by(models.Submenu.id
    ).first()
    
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found")

    submenu = query[0]
    submenu.dishes_count = query[1]

    return submenu


@router.post('/menus/{menu_id}/submenus', response_model=Submenu, status_code=status.HTTP_201_CREATED, tags=['submenu'])
def create_submenu(menu_id: int, submenu_data: SubmenuCreate, db: Session = Depends(get_session)) -> Submenu:
    menu = db.query(models.Menu
        ).filter(models.Menu.id == menu_id
        ).first()

    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="menu not found")

    submenu_db = models.Submenu(**submenu_data.dict())
    menu.submenus.append(submenu_db)
    db.commit()
    db.refresh(submenu_db)
    return submenu_db


@router.patch('/menus/{menu_id}/submenus/{submenu_id}', response_model=Submenu, tags=['submenu'])
def update_submenu(menu_id: int, submenu_id: int,submenu_data: SubmenuUpdate, db: Session = Depends(get_session)) -> Submenu:
    submenu = db.query(models.Submenu
        ).filter(models.Submenu.id == submenu_id
        ).filter(models.Submenu.menu_id == menu_id
        ).first()

    if not submenu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="menu not found")
    
    submenu.title = submenu_data.title if submenu_data.title else submenu.title
    submenu.description = submenu_data.description if submenu_data.description else submenu.description
    db.add(submenu)
    db.commit()
    db.refresh(submenu)

    return submenu
    

@router.delete('/menus/{menu_id}/submenus/{submenu_id}', status_code=status.HTTP_200_OK, tags=['submenu'])
def delete_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_session)):
    query = db.query(models.Submenu
        ).filter(models.Submenu.id == submenu_id
        ).filter(models.Submenu.menu_id == menu_id
        ).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found")
    
    db.delete(query)
    db.commit()

    return {"status": "true", "message": "The submenu has been deleted"}


###Dish###

@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=List[Dish], tags=['dish'])
def get_dish_list(menu_id: int, submenu_id: int, db: Session = Depends(get_session)) -> List[models.Dish]:
    dishes = db.query(models.Dish
        ).join(models.Submenu
        ).filter(models.Submenu.id == submenu_id, models.Submenu.menu_id == menu_id).all()

    return dishes


@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=Dish, tags=['dish'])
def get_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_session)) -> models.Dish:
    dish = db.query(models.Dish
        ).join(models.Submenu
        ).filter(models.Submenu.id == submenu_id,
                 models.Submenu.menu_id == menu_id,
                 models.Dish.id == dish_id).first()

    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dish not found")
    
    return dish


@router.post('/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=Dish, status_code=status.HTTP_201_CREATED,
             tags=['dish'])
def create_dish(menu_id: int, submenu_id: int, dish_data: DishCreate, db: Session = Depends(get_session)) -> Dish:
    submenu = db.query(models.Submenu
        ).filter(models.Submenu.id == submenu_id, models.Submenu.menu_id == menu_id
        ).first()
    
    dish_db = models.Dish(**dict(dish_data))
    submenu.dishes.append(dish_db)
    db.commit()
    db.refresh(dish_db)

    return dish_db


@router.patch('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=Dish, tags=['dish'])
def update_dish(menu_id: int, submenu_id: int, dish_id: int, dish_data: DishUpdate, db: Session = Depends(get_session)) -> Dish:
    dish = db.query(models.Dish
        ).join(models.Submenu
        ).filter(models.Submenu.id == submenu_id,
                 models.Submenu.menu_id == menu_id,
                 models.Dish.id == dish_id).first()
    
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dish not found")
    
    dish.title = dish_data.title if dish_data.title else dish.title
    dish.description = dish_data.description if dish_data.description else dish.description
    dish.price = dish_data.price if dish_data.price else dish.price
    db.add(dish)
    db.commit()
    db.refresh(dish)

    return dish


@router.delete('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', status_code=status.HTTP_200_OK,
               tags=['dish'])
def delete_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_session)):
    dish = db.query(models.Dish
        ).join(models.Submenu
        ).filter(models.Submenu.id == submenu_id,
                 models.Submenu.menu_id == menu_id,
                 models.Dish.id == dish_id).first()
    
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dish not found")
    
    db.delete(dish)
    db.commit()

    return {"status": "true", "message": "The dish has been deleted"}