from fastapi import APIRouter

from src.api.endpoints.task import router as task_router
from src.api.endpoints.user import router as user_router

router = APIRouter()
router.include_router(task_router)
router.include_router(user_router)
