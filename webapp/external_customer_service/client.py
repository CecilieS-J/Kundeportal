
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

external_engine = create_engine(
    str(settings.EXTERNAL_DATABASE_URL),
    echo=False,
    future=True
)

ExternalSession = sessionmaker(
    bind=external_engine,
    autoflush=False,
    autocommit=False
)
