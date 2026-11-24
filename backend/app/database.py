import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

logger = logging.getLogger("trafficintel.database")

Base = declarative_base()

engine = None
active_db_type = "sqlite"

try:
    if settings.DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        active_db_type = "sqlite"
    else:
        connect_args = {"connect_timeout": 3} if "pymysql" in settings.DATABASE_URL else {}
        temp_engine = create_engine(
            settings.DATABASE_URL,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        with temp_engine.connect() as conn:
            pass
        engine = temp_engine
        active_db_type = "mysql"
        logger.info("Successfully connected to MySQL database: %s", settings.DATABASE_URL.split("@")[-1])
except Exception as e:
    logger.warning("MySQL connection unavailable (%s). Falling back to SQLite: %s", e, settings.SQLITE_FALLBACK_URL)
    engine = create_engine(
        settings.SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False}
    )
    active_db_type = "sqlite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
