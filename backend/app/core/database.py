from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.models.base import Base
from app.core.config import settings

# engine is SQLAlchemy's database communication hub.
# engine doesn't itself "create a session." SessionLocal is what creates SQLAlchemy Session objects
# the Engine manages the database connectivity those sessions use

engine = create_engine(settings.database_url, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# Don't think: engine = create_engine(...) means: "Connect to PostgreSQL right now."
# Think: "Create the SQLAlchemy Engine that knows how to communicate with PostgreSQL using this connection configuration."
# Then when database work actually happens, the Engine handles the connections needed for that work.