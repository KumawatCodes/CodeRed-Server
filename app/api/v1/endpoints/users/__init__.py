from fastapi import APIRouter
from .show_users import router as show_router
from .online_users import router as online_router
from .upload_file import router as upload_file
router = APIRouter(prefix="/users", tags=["users"])


router.include_router(show_router)
router.include_router(online_router)
router.include_router(upload_file)