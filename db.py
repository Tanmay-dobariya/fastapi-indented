import os
from sqlalchemy import create_engine

# Use DATABASE_URL if available (e.g., on Render), otherwise fallback to local DB.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://<username>:<password>@localhost/<database_name>")

# Render often uses "postgres://" for URLs, but SQLAlchemy 1.4+ requires "postgresql://"
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(url=SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

