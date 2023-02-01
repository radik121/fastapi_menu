from pydantic import BaseModel


class SubmenuBase(BaseModel):

    title: str
    description: str | None

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'title': 'My submenu',
                'description': 'Submenu description',
            },
        }


class SubmenuCreate(SubmenuBase):
    pass


class SubmenuUpdate(SubmenuBase):
    pass


class Submenu(SubmenuBase):
    id: str
    dishes_count: int | None = 0

    class Config:
        schema_extra = {
            'example': {
                'title': 'My submenu',
                'description': 'Submenu description',
                'dishes count': 0,
            },
        }


class SubmenuDelete(BaseModel):

    status: str
    message: str

    class Config:
        schema_extra = {
            'example': {
                'status': 'true',
                'message': 'The submenu has been deleted',
            },
        }
