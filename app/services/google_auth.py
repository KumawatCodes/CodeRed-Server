from fastapi import HTTPException, status, Response
from sqlalchemy import select
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
FRONTEND_URL  = "http://localhost:3000"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

def get_google_auth_url():
    base = "https://accounts.google.com/o/oauth2/v2/auth"

    return (
        f"{base}"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
async def handle_google_callback(request, response: Response, db):

    code = request.query_params.get("code")

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )

    async with httpx.AsyncClient() as client:

        # 1️⃣ Exchange code for token
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        token_json = token_response.json()
        access_token = token_json.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )

        # 2️⃣ Fetch user info
        user_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        user_info = user_response.json()
        email = user_info.get("email")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email=email,
                first_name=user_info.get("name"),  # adjust if your model uses first_name/last_name
                auth_provider="google",
                google_id=user_info.get("id"),
                profile_picture=user_info.get("picture"),
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            redirect_url = f"{FRONTEND_URL}/app/profile"

        # CASE 2 — exists but profile incomplete
        elif not user.profile_complete:
            redirect_url = f"{FRONTEND_URL}/app/profile"

        # CASE 3 — verified user
        else:
            redirect_url = f"{FRONTEND_URL}/app/home"


        # set cookie
        # tokens = AuthService.create_user_tokens(user.user_id)



        # response.set_cookie(
        #     key="access_token",
        #     value=tokens["access_token"],
        #     httponly=True,
        #     secure=False,   # True in production
        #     samesite="lax",
        #     max_age=86400
        # )
        tokens = AuthService.create_user_tokens(user.user_id)
        response = RedirectResponse(redirect_url)
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="none",
            max_age=60 * 60 * 24
        )
        return response