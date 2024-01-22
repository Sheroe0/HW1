import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import MetaData, Column, String, Text, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Menu(Base):
    __tablename__ = "menus"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    title = Column(String)
    description = Column(Text)
    submenus = relationship("SubMenu", back_populates="menu", cascade="all, delete-orphan")


class SubMenu(Base):
    __tablename__ = "submenus"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    title = Column(String)
    description = Column(Text)
    menu_id = Column(UUID(as_uuid=True), ForeignKey("menus.id"))
    menu = relationship("Menu", back_populates="submenus")
    dishes = relationship("Dish", back_populates="submenu", cascade="all, delete-orphan")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    title = Column(String)
    description = Column(Text)
    price = Column(Numeric(precision=8, scale=2))
    submenu_id = Column(UUID(as_uuid=True), ForeignKey("submenus.id"))
    submenu = relationship("SubMenu", back_populates="dishes")