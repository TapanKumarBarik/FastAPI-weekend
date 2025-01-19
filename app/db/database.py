# app/db/database.py
from databases import Database
from sqlalchemy import create_engine, MetaData
from ..config import get_settings

settings = get_settings()

database = Database(settings.DATABASE_URL)
metadata = MetaData()

engine = create_engine(settings.DATABASE_URL)

