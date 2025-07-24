from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(self, obj_id: int, session: AsyncSession):
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        db_obj = result.scalars().first()
        if db_obj is None:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with id {obj_id} not found",
            )
        return db_obj

    async def get_multi(self, session: AsyncSession):
        db_objs = await session.execute(select(self.model))
        if db_objs is None:
            raise HTTPException(
                status_code=404,
                detail=f"No {self.model.__name__} records found",
            )
        return db_objs.scalars().all()

    async def create(self, obj_in, session: AsyncSession):
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        try:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Error while creating {self.model.__name__}",
            )

    async def update(self, db_obj, obj_in, session: AsyncSession):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        try:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Error while updating {self.model.__name__}",
            )

    async def remove(self, db_obj, session: AsyncSession):
        try:
            await session.delete(db_obj)
            await session.commit()
            return db_obj
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Error while deleting {self.model.__name__}",
            )
