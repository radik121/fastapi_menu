from sqlalchemy import Column, Identity, Integer, String
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    id = Column(Integer, Identity(always=True), primary_key=True)
    title = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(String(256))
