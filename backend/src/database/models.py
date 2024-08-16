from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)  # Username must be unique
    password = Column(String, nullable=False)

class ChatRoom(Base):
    __tablename__ = 'chatrooms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # ChatRoom name can be duplicated
    allowed_users = Column(Text)  # Stores as comma-separated string

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chatroom = Column(String, ForeignKey('chatrooms.name'), nullable=False)
    read_by = Column(Text)  # Stores as comma-separated string
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'text': self.text,
            'timestamp': self.timestamp.isoformat(),
            'chatroom': self.chatroom,
            'read_by': self.read_by.split(',') if self.read_by else []
        }


class Emoticon(Base):
    __tablename__ = 'emoticons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # Emoticon name can be duplicated
    url = Column(String, nullable=False)
    size = Column(String, nullable=False)  # small, medium, large
    animated = Column(Boolean, default=False)
    category = Column(String, nullable=False)
    chatroom = Column(String, ForeignKey('chatrooms.name'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'size': self.size,
            'animated': self.animated,
            'category': self.category,
            'chatroom': self.chatroom,
            'timestamp': self.timestamp.isoformat()
        }

class File(Base):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)  # Filename can be duplicated
    url = Column(String, nullable=False)
    version = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    chatroom = Column(String, ForeignKey('chatrooms.name'), nullable=False)
    edited_by = Column(Text)  # Stores as comma-separated string
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'url': self.url,
            'version': self.version,
            'uploaded_at': self.uploaded_at.isoformat(),
            'chatroom': self.chatroom,
            'edited_by': self.edited_by.split(',') if self.edited_by else []
        }
    
