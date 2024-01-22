from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

from database import get_async_session
from models import Base, SubMenu, Dish

submenu_router = APIRouter(prefix="/api/v1/menus/{target_menu_id}/submenus")


class SubMenuInput(BaseModel):
    title: str
    description: str


class SubMenuOutput(BaseModel):
    id: UUID
    title: str
    description: str
    dishes_count: int
    menu_id: UUID


class SubMenuUpdate(BaseModel):
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


async def get_counts_for_submenu(submenu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    dishes_count = await session.scalar(select(func.count(Dish.id)).join(SubMenu).where(Dish.submenu_id == submenu_id))
    return dishes_count


@submenu_router.get("/", response_model=List[SubMenuOutput])
async def get_all_submenus(target_menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(SubMenu).where(SubMenu.menu_id == target_menu_id)
    result = await session.execute(query)
    submenus_with_counts = []
    for submenu_tuple in result.all():
        submenu = submenu_tuple[0]
        submenu.dishes_count = await get_counts_for_submenu(submenu.id, session)
        submenus_with_counts.append(submenu)
    return submenus_with_counts


@submenu_router.get("/{target_submenu_id}", response_model=SubMenuOutput)
async def get_specific_submenu(target_submenu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    submenu = await get_object_by_id(target_submenu_id, SubMenu, session)
    submenu.dishes_count = await get_counts_for_submenu(submenu.id, session)
    return submenu


@submenu_router.patch("/{target_submenu_id}", response_model=SubMenuOutput)
async def update_submenu( target_submenu_id: UUID, updated_data: SubMenuUpdate, session: AsyncSession = Depends(get_async_session)):
    submenu = await get_object_by_id(target_submenu_id, SubMenu, session)
    for field, value in updated_data.model_dump().items():
        if value is not None:
            setattr(submenu, field, value)
    await session.commit()
    await session.refresh(submenu)
    submenu.dishes_count = await get_counts_for_submenu(submenu.id, session)
    return submenu


@submenu_router.post("/", status_code=status.HTTP_201_CREATED, response_model=SubMenuOutput)
async def create_submenu(target_menu_id: UUID, new_submenu: SubMenuInput, session: AsyncSession = Depends(get_async_session)):
    stmt = (insert(SubMenu).values(menu_id=target_menu_id, **new_submenu.model_dump()).returning(SubMenu))
    result = await session.execute(stmt)
    submenu = result.fetchone()[0]
    await session.commit()
    submenu.dishes_count = await get_counts_for_submenu(submenu.id, session)
    return submenu


@submenu_router.delete("/{target_submenu_id}")
async def delete_submenu(target_submenu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    submenu = await get_object_by_id(target_submenu_id, SubMenu, session)
    await session.delete(submenu)
    await session.commit()