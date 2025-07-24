from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_user
from src.crud.task import task_crud
from src.schemas.task import TaskCreate, TaskResponse, TaskStatus, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/",
    response_model=list[TaskResponse],
    dependencies=[Depends(current_user)],
)
async def read_tasks(
    session: AsyncSession = Depends(get_async_session),
    status: TaskStatus | None = Query(
        None, description="Filter by task status"
    ),
):
    result = await task_crud.get_multi(session=session, status=status)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No tasks found",
        )
    return result


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(current_user)],
)
async def read_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    return await task_crud.get(obj_id=task_id, session=session)


@router.post(
    "/",
    response_model=TaskResponse,
    dependencies=[Depends(current_user)],
)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await task_crud.create(obj_in=data, session=session)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(current_user)],
)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    db_obj = await task_crud.get(obj_id=task_id, session=session)
    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return await task_crud.update(db_obj=db_obj, obj_in=data, session=session)


@router.delete(
    "/{task_id}",
    dependencies=[Depends(current_user)],
)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    db_obj = await task_crud.get(obj_id=task_id, session=session)
    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    await task_crud.remove(db_obj=db_obj, session=session)
    return {"message": "Task deleted successfully"}
