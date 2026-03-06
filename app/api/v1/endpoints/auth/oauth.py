from fastapi import APIRouter,Depends,Request,Response
from fastapi.responses import RedirectResponse
from app.services.google_auth import get_google_auth_url,handle_google_callback
from app.database import get_db
from app.schemas.auth import AuthResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
router = APIRouter()

@router.get("/google/login")
async def google_login():
    url = get_google_auth_url()
    print(url)
    return RedirectResponse(url)


@router.get("/google/callback", response_model=AuthResponse)
async def google_callback(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    return await handle_google_callback(request, response, db)