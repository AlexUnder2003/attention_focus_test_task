from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    class Config:
        from_attributes = True


class TaskResponse(TaskCreate):
    id: int
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True
