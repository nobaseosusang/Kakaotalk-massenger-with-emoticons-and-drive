from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class ChatRoom(Base):
    __tablename__ = 'chatrooms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    allowed_users = Column(Text)  # Stores as comma-separated string

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chatroom = Column(String, ForeignKey('chatrooms.name'), nullable=False)
    read_by = Column(Text)  # Stores as comma-separated string

class Emoticon(Base):
    __tablename__ = 'emoticons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    size = Column(String, nullable=False)  # small, medium, large
    animated = Column(Boolean, default=False)
    category = Column(String, nullable=False)
    chatroom = Column(String, ForeignKey('chatrooms.name'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class File(Base):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    version = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    chatroom = Column(String, ForeignKey('chatrooms.name'), nullable=False)
    edited_by = Column(Text)  # Stores as comma-separated string
