import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from datetime import timedelta
load_dotenv()



class Settings(BaseSettings):
     # Secret key with a fallback for development environments
    SECRET_KEY: str = "fallback-til-dev"

     # Main database for login and user-related data.
    # Will use DATABASE_URL from .env if available, otherwise defaults to local SQLite file.
    DATABASE_URL: AnyUrl = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "instance",
            "customer_data.db",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MDM_DATABASE_URL: AnyUrl  

    # Session/Cookie settings for security and expiration
    SESSION_PERMANENT: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SECURE: bool = True
    REMEMBER_COOKIE_HTTPONLY: bool = True
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(minutes=30)

    # Mailgun HTTP API credentials
    MAILGUN_DOMAIN: str              
    MAILGUN_API_KEY: str     

    # 🔽 Brevo settings
    BREVO_API_KEY: str

    # 🔽 SFCC settings (til token)
    SFCC_CLIENT_ID: str
    SFCC_CLIENT_SECRET: str
    SFCC_USER: str
    SFCC_PASSWORD: str
    SFCC_AUTH_TYPE: str 
    SFCC_INSTANCE: str


    # 🔽 Omneo settings
    OMNEO_API_TOKEN: str
    OMNEO_BASE_URL: str

        
    smseagle_url: str
    smseagle_user: str
    smseagle_pass: str

    

    class Config:
        # Configuration for loading environment variables from the .env file
        env_file = ".env"
        env_file_encoding = "utf-8"

# Single global instance of Settings
settings = Settings()

# ✅ Legacy alias-style (til din gamle codebase)
sfcc_client_id = settings.SFCC_CLIENT_ID
sfcc_secret = settings.SFCC_CLIENT_SECRET
sfcc_user = settings.SFCC_USER
sfcc_password = settings.SFCC_PASSWORD
sfcc_authType = settings.SFCC_AUTH_TYPE
sfcc_instance = settings.SFCC_INSTANCE