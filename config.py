from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()  # læs variabler fra .env ind i os.environ



basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or "fallback-til-dev"


    # Brug instance-mappen til din DB‐fil
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(basedir, "instance", "customer_data.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE    = True    # Kun send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY  = True    # Forhindrer JS i at læse cookie
    REMEMBER_COOKIE_SECURE   = True
    REMEMBER_COOKIE_HTTPONLY = True

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

