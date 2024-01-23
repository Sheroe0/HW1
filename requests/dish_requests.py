from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_async_session
from models import Base, Dish
from pydantic import BaseModel

dish_router = APIRouter(prefix="/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes")


class DishInput(BaseModel):
    title: str
    description: str
    price: float


class DishOutput(BaseModel):
    id: UUID
    title: str
    description: str
    price: str
    submenu_id: UUID


class DishUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


async def get_object_by_id(target_object_id: UUID, object: Base, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(object).where(object.id == target_object_id))
    entity = result.scalar()
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{object.__name__.lower()} not found",
        )
    return entity


def convert_price(dish: dict):
    dish.price = str(dish.price)
    return dish


@dish_router.get("/", response_model=List[DishOutput])
async def get_all_dishes(target_submenu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).where(Dish.submenu_id == target_submenu_id)
    result = await session.execute(query)
    dishes = [convert_price(dish_tuple[0]) for dish_tuple in result.all()]
    return dishes


@dish_router.get("/{target_dish_id}", response_model=DishOutput)
async def get_specific_dish(target_dish_id: UUID, session: AsyncSession = Depends(get_async_session)):
    dish = await get_object_by_id(target_dish_id, Dish, session)
    return convert_price(dish)


@dish_router.patch("/{target_dish_id}", response_model=DishOutput)
async def update_dish(target_dish_id: UUID, updated_data: DishUpdate, session: AsyncSession = Depends(get_async_session)):
    dish = await get_object_by_id(target_dish_id, Dish, session)
    for field, value in updated_data.model_dump().items():
        if value is not None:
            setattr(dish, field, value)
    await session.commit()
    await session.refresh(dish)
    return convert_price(dish)


@dish_router.post("/", status_code=status.HTTP_201_CREATED, response_model=DishOutput)
async def create_dish(target_submenu_id: UUID, new_dish: DishInput, session: AsyncSession = Depends(get_async_session)):
    stmt = (insert(Dish).values(submenu_id=target_submenu_id, **new_dish.model_dump()).returning(Dish))
    result = await session.execute(stmt)
    dish = result.fetchone()[0]
    await session.commit()
    return convert_price(dish)


@dish_router.delete("/{target_dish_id}")
async def delete_dish(target_dish_id: UUID, session: AsyncSession = Depends(get_async_session)):
    dish = await get_object_by_id(target_dish_id, Dish, session)
    await session.delete(dish)
    await session.commit()