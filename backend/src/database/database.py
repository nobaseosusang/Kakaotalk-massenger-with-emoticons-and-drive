from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from src.database.models import Base

from config import config


engine = create_engine(config.DATABASE_URI)
session = sessionmaker(bind=engine)

def get_db():
    return session()