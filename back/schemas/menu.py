from pydantic import BaseModel


class MenuBase(BaseModel):

    title: str
    description: str | None

    class Config:
        orm_mode = True


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    pass


class Menu(MenuBase):
    id: str
    submenus_count: int | None = 0
    dishes_count: int | None = 0

    # class Config:
    #     orm_mode = True
