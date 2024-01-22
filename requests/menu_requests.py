from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

from database import get_async_session
from models import Menu, SubMenu, Dish, Base


menu_router = APIRouter(prefix="/api/v1/menus")


class MenuIn(BaseModel):
    title: str
    description: str


class MenuOut(BaseModel):
    id: UUID
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuUp(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


async def get_object_by_id(target_object_id: UUID, object: Base, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(object).where(object.id == target_object_id))
    entity = result.scalar()
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{object.__name__.lower()} not found",
        )
    return entity


async def get_counts_for_menu(menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    submenus_count = await session.scalar(select(func.count(SubMenu.id)).join(Menu).where(SubMenu.menu_id == menu_id))
    dishes_count = await session.scalar(select(func.count(Dish.id)).join(SubMenu).join(Menu).where(SubMenu.menu_id == menu_id))
    return submenus_count, dishes_count


@menu_router.get("/", response_model=List[MenuOut])
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu)
    result = await session.execute(query)
    menus_with_counts = []
    for menu_tuple in result.all():
        menu = menu_tuple[0]
        menu.submenus_count, menu.dishes_count = await get_counts_for_menu(menu.id, session)
        menus_with_counts.append(menu)
    return menus_with_counts


@menu_router.get("/{target_menu_id}", response_model=MenuOut)
async def get_specific_menu(target_menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    menu = await get_object_by_id(target_menu_id, Menu, session)
    menu.submenus_count, menu.dishes_count = await get_counts_for_menu(menu.id, session)
    return menu


@menu_router.patch("/{target_menu_id}", response_model=MenuOut)
async def update_menu(target_menu_id: UUID, updated_data: MenuUp, session: AsyncSession = Depends(get_async_session)):
    menu = await get_object_by_id(target_menu_id, Menu, session)
    for field, value in updated_data.model_dump().items():
        if value is not None:
            setattr(menu, field, value)
    await session.commit()
    await session.refresh(menu)
    menu.submenus_count, menu.dishes_count = await get_counts_for_menu(menu.id, session)
    return menu


@menu_router.post("/", status_code=status.HTTP_201_CREATED, response_model=MenuOut)
async def create_menu(new_menu: MenuIn, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Menu).values(**new_menu.model_dump()).returning(Menu)
    result = await session.execute(stmt)
    menu = result.fetchone()[0]
    await session.commit()
    menu.submenus_count, menu.dishes_count = await get_counts_for_menu(menu.id, session)
    return menu


@menu_router.delete("/{target_menu_id}")
async def delete_menu(target_menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    menu = await get_object_by_id(target_menu_id, Menu, session)
    await session.delete(menu)
    await session.commit()