import os
from dotenv import load_dotenv
# Load .env i projektroot
load_dotenv()
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from datetime import timedelta


class Settings(BaseSettings):
    # Secret key med dev-fallback
    SECRET_KEY: str = "fallback-til-dev"

    # Database: brug .env eller fald tilbage til instance/customer_data.db
    DATABASE_URL: AnyUrl = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "instance",
            "customer_data.db",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    EXTERNAL_DATABASE_URL: AnyUrl  

    # Session/Cookie-indstillinger
    SESSION_PERMANENT: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SECURE: bool = True
    REMEMBER_COOKIE_HTTPONLY: bool = True
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(minutes=30)

    

    # Mailgun HTTP API
    MAILGUN_DOMAIN: str              # f.eks. "sandbox…mailgun.org"
    MAILGUN_API_KEY: str             # f.eks. "key-…"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Én global instans
settings = Settings()
