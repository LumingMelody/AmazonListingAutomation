from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


def create_sqlalchemy_engine(database_url: str | None = None):
    """Create SQLAlchemy engine with sensible defaults."""
    url = database_url or settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, future=True, connect_args=connect_args)


engine = create_sqlalchemy_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=Session)


def get_db(session_factory: sessionmaker | None = None) -> Generator[Session, None, None]:
    factory = session_factory or SessionLocal
    db = factory()
    try:
        yield db
    finally:
        db.close()


def check_database_connection(session_factory: sessionmaker | None = None) -> bool:
    factory = session_factory or SessionLocal
    try:
        with factory() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

