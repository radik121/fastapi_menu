from pydantic import BaseModel


class DishBase(BaseModel):
    title: str
    description: str | None
    price: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "My dish",
                "description": "Dish description",
                "price": "10.50",
            },
        }


class DishCreate(DishBase):
    pass


class DishUpdate(DishBase):
    pass


class Dish(DishBase):
    id: str


class DishDelete(BaseModel):
    status: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "status": "true",
                "message": "The dish has been deleted",
            },
        }
