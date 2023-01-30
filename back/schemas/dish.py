from pydantic import BaseModel


class DishBase(BaseModel):

    title: str
    description: str | None
    price: str

    class Config:
        orm_mode = True


class DishCreate(DishBase):
    pass


class DishUpdate(DishBase):
    pass


class Dish(DishBase):
    id: str
