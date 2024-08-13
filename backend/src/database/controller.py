from src.database.models import User, ChatRoom, Message, Emoticon, File
from src.database.database import Database
from datetime import datetime
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash

db = Database()

def register_user(username: str, password: str):
    session = db.get_session()
    
    try:
        # 사용자 이름 중복 체크
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return None, "Username already exists"

        # 새 사용자 추가
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        session.add(user)
        session.commit()

        # 사용자 데이터를 세션 종료 전에 미리 추출
        user_data = {'username': user.username}

        return user_data, None
    finally:
        session.close()

def authenticate_user(username: str, password: str) -> bool:
    session = db.get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return True
        return False
    finally:
        session.close()

def create_chatroom(name: str, allowed_users: List[str]):
    session = db.get_session()
    try:
        # 새 채팅방 추가
        chatroom = ChatRoom(name=name, allowed_users=','.join(allowed_users))
        session.add(chatroom)
        session.commit()
        return chatroom, None
    finally:
        session.close()

def send_message(username: str, text: str, chatroom: str):
    session = db.get_session()
    try:
        room = session.query(ChatRoom).filter_by(name=chatroom).first()
        if room and username in room.allowed_users.split(','):
            message = Message(username=username, text=text, timestamp=datetime.now(), chatroom=chatroom)
            session.add(message)
            session.commit()
            return message, None
        raise PermissionError("User not allowed in this chatroom")
    finally:
        session.close()

def get_messages(chatroom: str):
    session = db.get_session()
    try:
        room = session.query(ChatRoom).filter_by(name=chatroom).first()
        if room:
            messages = session.query(Message).filter_by(chatroom=chatroom).all()
            return messages, None
        raise PermissionError("Chatroom not found or access denied")
    finally:
        session.close()

def add_emoticon(name: str, url: str, size: str, animated: bool, category: str, chatroom: str):
    session = db.get_session()
    try:
        # 새 이모티콘 추가 (중복 검사 없음)
        emoticon = Emoticon(name=name, url=url, size=size, animated=animated, category=category, chatroom=chatroom)
        session.add(emoticon)
        session.commit()
        return emoticon, None
    finally:
        session.close()

def get_emoticons(category: str):
    session = db.get_session()
    try:
        if category:
            emoticons = session.query(Emoticon).filter_by(category=category).all()
        else:
            emoticons = session.query(Emoticon).all()
        return emoticons, None
    finally:
        session.close()

def upload_file(filename: str, url: str, edited_by: List[str], chatroom: str):
    session = db.get_session()
    try:
        # 새 파일 추가 (중복 검사 없음)
        file = File(filename=filename, url=url, version=1, uploaded_at=datetime.now(), chatroom=chatroom, edited_by=','.join(edited_by))
        session.add(file)
        session.commit()
        return file, None
    finally:
        session.close()

def update_file_version(filename: str, new_url: str, edited_by: List[str], chatroom: str):
    session = db.get_session()
    try:
        existing_files = session.query(File).filter_by(filename=filename, chatroom=chatroom).order_by(File.version.desc()).all()
        if not existing_files:
            return None, "File not found"
        
        new_version = existing_files[0].version + 1

        file = File(
            filename=filename, 
            url=new_url, 
            version=new_version, 
            uploaded_at=datetime.now(), 
            chatroom=chatroom, 
            edited_by=','.join(edited_by)
        )
        session.add(file)
        session.commit()
        return file, None
    finally:
        session.close()

def get_room_data(chatroom: str):
    session = db.get_session()
    try:
        room = session.query(ChatRoom).filter_by(name=chatroom).first()
        if room:
            messages = session.query(Message).filter_by(chatroom=chatroom).all()
            emoticons = session.query(Emoticon).filter_by(chatroom=chatroom).all()
            files = session.query(File).filter_by(chatroom=chatroom).all()
            
            combined_data = messages + emoticons + files
            combined_data.sort(key=lambda x: x.timestamp)
            
            return combined_data, None
        raise PermissionError("Chatroom not found or access denied")
    finally:
        session.close()
