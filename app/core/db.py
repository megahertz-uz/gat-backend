from sqlmodel import create_engine, SQLModel
from sqlalchemy import inspect
import logging
from app.core.config import settings

try:
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    logging.info("Successfully connected to the database.")

    inspector = inspect(engine)
    if not inspector.has_table("user"):
        logging.info("Table 'user' does not exist. Creating all tables.")
        SQLModel.metadata.create_all(engine)
    else:
        logging.info("Table 'user' already exists. Skipping table creation.")
except Exception as e:
    logging.error(f"Failed to initialize database connection: {e}")
    raise e
