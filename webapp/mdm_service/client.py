
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

mdm_engine = create_engine(
    str(settings.MDM_DATABASE_URL),
    echo=False,
    future=True
)

MdmSession = sessionmaker(
    bind=mdm_engine,
    autoflush=False,
    autocommit=False
)
