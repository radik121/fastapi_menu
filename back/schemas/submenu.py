from typing import Optional, Union
from pydantic import BaseModel


class SubmenuBase(BaseModel):

    title: str
    description: Optional[str]

    class Config:
        orm_mode = True


class SubmenuCreate(SubmenuBase):
    pass


class SubmenuUpdate(SubmenuBase):
    pass


class Submenu(SubmenuBase):
    id: str
    dishes_count: Optional[int] = 0

    # class Config:
    #     orm_mode = True