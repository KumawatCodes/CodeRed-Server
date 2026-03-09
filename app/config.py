from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Google OAuth
    GOOGLE_CLIENT_ID: str 
    GOOGLE_CLIENT_SECRET: str 
    GOOGLE_REDIRECT_URI: str 

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    PISTON_API_URL: str
    # APIs
    GOOGLE_API_KEY: str
    # Application
    PROJECT_NAME: str = "CodeRed"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"


    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()