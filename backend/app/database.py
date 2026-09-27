import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# SQLite compatibility settings vs PostgreSQL/PostGIS
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for providing database sessions in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all database tables defined by SQLAlchemy models and perform idempotent column migrations."""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            if settings.DATABASE_URL.startswith("sqlite"):
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE incidents ADD COLUMN location_name TEXT DEFAULT 'Unknown Marine Region';"))
                conn.commit()
    except Exception:
        pass

