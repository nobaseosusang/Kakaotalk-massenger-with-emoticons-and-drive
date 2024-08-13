from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base



class Database:
    def __init__(self, database_url='sqlite:///chat_app.db'):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
