from pydantic import BaseModel


class MenuBase(BaseModel):

    title: str
    description: str | None

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'title': 'My menu',
                'description': 'Menu description',
            },
        }


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    pass


class Menu(MenuBase):
    id: str
    submenus_count: int | None = 0
    dishes_count: int | None = 0

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'title': 'My menu',
                'description': 'Menu description',
                'submenus_count': 0,
                'dishes_count': 0,
            },
        }


class MenuDelete(BaseModel):
    class Config:
        schema_extra = {
            'example': {
                'status': 'true',
                'message': 'The menu has been deleted',
            },
        }
