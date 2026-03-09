from fastapi import APIRouter
from .login import router as login_router
from .register import router as register_router

# from .profile import router as profile_router
# from .email_check import router as email_check_router
# from .google import router as google_router
#  # Add this import

from .profile import router as profile_router
from .oauth import router as google_login
router = APIRouter(prefix="/auth", tags=["authentication"])

# Include all auth routers
router.include_router(login_router)
router.include_router(register_router)

# router.include_router(profile_router)
# router.include_router(email_check_router)
# router.include_router(google_router) # Add this line

router.include_router(profile_router)
router.include_router(google_login)
