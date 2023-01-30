from fastapi import APIRouter

from .router import router as operations_router

router = APIRouter()
router.include_router(operations_router)
