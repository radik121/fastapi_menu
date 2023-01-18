from typing import Optional, Union
from pydantic import BaseModel


class MenuBase(BaseModel):

    title: str
    description: Optional[str]

    class Config:
        orm_mode = True


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    pass


class Menu(MenuBase):
    id: str
    submenus_count: Optional[int] = 0
    dishes_count: Optional[int] = 0

    # class Config:
    #     orm_mode = True