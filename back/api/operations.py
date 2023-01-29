from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func

from schemas.menu import MenuCreate, Menu, MenuUpdate
from schemas.submenu import Submenu, SubmenuCreate, SubmenuUpdate
from schemas.dish import Dish, DishCreate, DishUpdate
from db import models


def not_found_404(value: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{value} not found")


class Menu:
    """Requests by menu"""

    def get_list(self, db: Session):
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


    def get_id_menu(self, menu_id: int, db: Session):
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
            not_found_404('menu')

        menu = query[0]
        menu.submenus_count = query[1]
        menu.dishes_count = query[2]
        
        return menu    
    

    def create(self, menu_data: MenuCreate, db: Session):
        menu_db = models.Menu(**menu_data.dict())
        db.add(menu_db)
        db.commit()
        db.refresh(menu_db)
        return menu_db


    def update(self, menu_id: int, menu_data: MenuUpdate, db: Session):
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
            not_found_404('menu')

        menu = query[0]
        menu.submenus_count = query[1]
        menu.dishes_count = query[2]
        menu.title = menu_data.title if menu_data.title else menu.title
        menu.description = menu_data.description if menu_data.description else menu.description
        db.add(menu)
        db.commit()
        db.refresh(menu)
        
        return menu


    def delete(self, menu_id: int, db: Session):
        query = db.query(models.Menu).filter(models.Menu.id == menu_id).first()

        if not query:
            not_found_404('menu')
        
        db.delete(query)
        db.commit()

        return {"status": "true", "message": "The menu has been deleted"}



class Submenu:
    """Requests by submenu"""

    def get_list(self, menu_id: int, db: Session):
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


    def get_id_submenu(self, menu_id: int, submenu_id: int, db: Session):
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
            not_found_404('submenu')

        submenu = query[0]
        submenu.dishes_count = query[1]

        return submenu


    def create(self, menu_id: int, submenu_data: SubmenuCreate, db: Session):
        menu = db.query(models.Menu
            ).filter(models.Menu.id == menu_id
            ).first()

        if not menu:
            not_found_404('submenu')

        submenu_db = models.Submenu(**submenu_data.dict())
        menu.submenus.append(submenu_db)
        db.commit()
        db.refresh(submenu_db)
        return submenu_db


    def update(self, menu_id: int, submenu_id: int, submenu_data: SubmenuUpdate, db: Session):
        submenu = db.query(models.Submenu
            ).filter(models.Submenu.id == submenu_id
            ).filter(models.Submenu.menu_id == menu_id
            ).first()

        if not submenu:
            not_found_404('submenu')
        
        submenu.title = submenu_data.title if submenu_data.title else submenu.title
        submenu.description = submenu_data.description if submenu_data.description else submenu.description
        db.add(submenu)
        db.commit()
        db.refresh(submenu)

        return submenu
    

    def delete(self, menu_id: int, submenu_id: int, db: Session):
        query = db.query(models.Submenu
            ).filter(models.Submenu.id == submenu_id
            ).filter(models.Submenu.menu_id == menu_id
            ).first()

        if not query:
            not_found_404('submenu')
        
        db.delete(query)
        db.commit()

        return {"status": "true", "message": "The submenu has been deleted"}



class Dish:
    """Requests by dish"""

    def get_list(self, menu_id: int, submenu_id: int, db: Session):
        dishes = db.query(models.Dish
            ).join(models.Submenu
            ).filter(
                models.Submenu.id == submenu_id,
                models.Submenu.menu_id == menu_id
            ).all()

        return dishes


    def get_id_dish(self, menu_id: int, submenu_id: int, dish_id: int, db: Session):
        dish = db.query(models.Dish
            ).join(models.Submenu
            ).filter(
                models.Submenu.id == submenu_id,
                models.Submenu.menu_id == menu_id,
                models.Dish.id == dish_id
            ).first()

        if not dish:
            not_found_404('dish')
        
        return dish


    def create(self, menu_id: int, submenu_id: int, dish_data: DishCreate, db: Session):
        submenu = db.query(models.Submenu
            ).filter(models.Submenu.id == submenu_id, models.Submenu.menu_id == menu_id
            ).first()
        
        dish_db = models.Dish(**dict(dish_data))
        submenu.dishes.append(dish_db)
        db.commit()
        db.refresh(dish_db)

        return dish_db


    def update(self, menu_id: int, submenu_id: int, dish_id: int, dish_data: DishUpdate, db: Session):
        dish = db.query(models.Dish
            ).join(models.Submenu
            ).filter(models.Submenu.id == submenu_id,
                    models.Submenu.menu_id == menu_id,
                    models.Dish.id == dish_id).first()
        
        if not dish:
            not_found_404('dish')
        
        dish.title = dish_data.title if dish_data.title else dish.title
        dish.description = dish_data.description if dish_data.description else dish.description
        dish.price = dish_data.price if dish_data.price else dish.price
        db.add(dish)
        db.commit()
        db.refresh(dish)

        return dish


    def delete(self, menu_id: int, submenu_id: int, dish_id: int, db: Session):
        dish = db.query(models.Dish
            ).join(models.Submenu
            ).filter(models.Submenu.id == submenu_id,
                    models.Submenu.menu_id == menu_id,
                    models.Dish.id == dish_id).first()
        
        if not dish:
            not_found_404('dish')
        
        db.delete(dish)
        db.commit()

        return {"status": "true", "message": "The dish has been deleted"}


menu = Menu()
submenu = Submenu()
dish = Dish()