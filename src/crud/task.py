from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.task import Task


class CRUDTask(CRUDBase):
    async def get_multi(
        self,
        session: AsyncSession,
        status: str | None = None,
    ):
        query = select(self.model)
        if status:
            query = query.where(self.model.status == status)
        db_objs = await session.execute(query)
        if db_objs is None:
            raise HTTPException(
                status_code=404,
                detail=f"No {self.model.__name__} records found",
            )
        return db_objs.scalars().all()


task_crud = CRUDTask(Task)
