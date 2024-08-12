from models import User, ChatRoom, Message, Emoticon, File
from database import Database
from datetime import datetime
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash

db = Database()

def register_user(username: str, password: str):
    session = db.get_session()
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    session.add(user)
    session.commit()
    return user

def authenticate_user(username: str, password: str) -> bool:
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):  # 여기서 user.password는 str 값임
        return True
    return False


def create_chatroom(name: str, allowed_users: List[str]):
    session = db.get_session()
    chatroom = ChatRoom(name=name, allowed_users=','.join(allowed_users))
    session.add(chatroom)
    session.commit()
    return chatroom

def send_message(username: str, text: str, chatroom: str):
    session = db.get_session()

    room = session.query(ChatRoom).filter_by(name=chatroom).first()
    if room and username in room.allowed_users.split(','):
        message = Message(username=username, text=text, timestamp=datetime.now(), chatroom=chatroom)
        session.add(message)
        session.commit()
        return message
    raise PermissionError("User not allowed in this chatroom")

def get_messages(chatroom: str):
    session = db.get_session()
    room = session.query(ChatRoom).filter_by(name=chatroom).first()
    if room:
        messages = session.query(Message).filter_by(chatroom=chatroom).all()
        return messages
    raise PermissionError("Chatroom not found or access denied")

def add_emoticon(name: str, url: str, size: str, animated: bool, category: str, chatroom: str):
    session = db.get_session()
    emoticon = Emoticon(name=name, url=url, size=size, animated=animated, category=category, chatroom=chatroom)
    session.add(emoticon)
    session.commit()
    return emoticon

def get_emoticons(category: str):
    session = db.get_session()
    if category:
        emoticons = session.query(Emoticon).filter_by(category=category).all()
    else:
        emoticons = session.query(Emoticon).all()
    return emoticons

def upload_file(filename: str, url: str, edited_by: List[str], chatroom: str):
    session = db.get_session()
    file = File(filename=filename, url=url, version=1, uploaded_at=datetime.now(), chatroom=chatroom, edited_by=','.join(edited_by))
    session.add(file)
    session.commit()
    return file

def update_file_version(filename: str, new_url: str, edited_by: List[str], chatroom: str):
    session = db.get_session()
    
    # 기존 파일 검색
    existing_files = session.query(File).filter_by(filename=filename, chatroom=chatroom).order_by(File.version.desc()).all()
    if not existing_files:
        return None  # 파일이 존재하지 않으면 None 반환
    
    # 새로운 버전을 추가
    new_version = existing_files[0].version + 1

    # 새로운 파일 버전을 추가하며, 기존 파일을 유지
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
    session.close()
    return file

def get_room_data(chatroom: str):

    session = db.get_session()
    room = session.query(ChatRoom).filter_by(name=chatroom).first()
    if room:
        messages = session.query(Message).filter_by(chatroom=chatroom).all()
        emoticons = session.query(Emoticon).filter_by(chatroom=chatroom).all()
        files = session.query(File).filter_by(chatroom=chatroom).all()
        
        # Combine all data
        combined_data = messages + emoticons + files

        # Sort by datetime attribute
        combined_data.sort(key=lambda x: x.datetime)

        session.close()
        return combined_data

    session.close()
    raise PermissionError("Chatroom not found or access denied")
