from decimal import Decimal
from typing import Optional, Union
from pydantic import BaseModel


class DishBase(BaseModel):

    title: str
    description: Optional[str]
    price: str

    class Config:
        orm_mode = True


class DishCreate(DishBase):
    pass


class DishUpdate(DishBase):
    pass


class Dish(DishBase):
    id: str