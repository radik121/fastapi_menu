from db.base import Base
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship


class Menu(Base):
    __tablename__ = 'menu'

    submenus = relationship(
        'Submenu', back_populates='menu', cascade='all, delete',
    )


class Submenu(Base):
    __tablename__ = 'submenu'

    menu_id = Column(
        Integer, ForeignKey(
            'menu.id', ondelete='CASCADE',
        ), nullable=False,
    )

    menu = relationship('Menu', back_populates='submenus')
    dishes = relationship(
        'Dish', back_populates='submenu', cascade='all, delete',
    )


class Dish(Base):
    __tablename__ = 'dich'

    price = Column(Numeric(10, 2), index=True)
    submenu_id = Column(
        Integer, ForeignKey(
            'submenu.id', ondelete='CASCADE',
        ), nullable=False,
    )

    submenu = relationship('Submenu', back_populates='dishes')
