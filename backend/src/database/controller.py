from sqlalchemy.orm import Session
from src.database.models import User, ChatRoom, Message, Emoticon, File
from datetime import datetime
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash



def register_user(db : Session, username: str, password: str):
    existing_user = db.query(User).filter(User.username==username).first()
    if existing_user:
        return None, "Username already exists"

    # 새 사용자 추가
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()

    # 사용자 데이터를 세션 종료 전에 미리 추출
    user_data = {'username': user.username}

    return user_data, None

def authenticate_user(db: Session, username: str, password: str) -> bool:
    user = db.query(User).filter(User.username==username).first()
    if user and check_password_hash(user.password, password):
        return True
    return False

def create_chatroom(db:Session, name: str, allowed_users: List[str]):
    chatroom = ChatRoom(name=name, allowed_users=','.join(allowed_users))
    db.add(chatroom)
    db.commit()

    chatroom_data = {'name': chatroom.name, 'id': chatroom.id}

    return chatroom_data, None

def send_message(db:Session, username: str, text: str, chatroom: str):
    room = db.query(ChatRoom).filter(ChatRoom.name==chatroom).first()
    if room and username in room.allowed_users.split(','):
        message = Message(username=username, text=text, timestamp=datetime.now(), chatroom=chatroom)
        db.add(message)
        db.commit()

        # 세션이 닫히기 전에 필요한 데이터를 미리 추출
        message_data = {
            'id': message.id,
            'username': message.username,
            'text': message.text,
            'timestamp': message.timestamp.isoformat(),  # datetime을 문자열로 변환
            'chatroom': message.chatroom,
            'read_by': message.read_by.split(',') if message.read_by else []
        }
        return message_data, None
    
    raise PermissionError("User not allowed in this chatroom")


def get_messages(db:Session, chatroom: str):
    room = db.query(ChatRoom).filter(ChatRoom.name==chatroom).first()
    if room:
        messages = db.query(Message).filter(Message.chatroom==chatroom).all()
        return messages, None
    raise PermissionError("Chatroom not found or access denied")

def add_emoticon(db:Session, name: str, url: str, size: str, animated: bool, category: str, chatroom: str):
    emoticon = Emoticon(name=name, url=url, size=size, animated=animated, category=category, chatroom=chatroom)
    db.add(emoticon)
    db.commit()
    emoticon_data = emoticon.to_dict()
    return emoticon_data, None


def get_emoticons(db:Session, category: str = None):
    if category:
        emoticons = db.query(Emoticon).filter_by(Emoticon.category==category).all()
    else:
        emoticons = db.query(Emoticon).all()
    
    return emoticons, None


def send_emoticon(db:Session, username: str, emoticon_id: int, chatroom: str):
    # 채팅방과 이모티콘 찾기
    room = db.query(ChatRoom).filter_by(name=chatroom).first()
    emoticon = db.query(Emoticon).filter_by(id=emoticon_id).first()

    if not room or not emoticon:
        return None, "Chatroom or Emoticon not found"

    if username not in room.allowed_users.split(','):
        return None, "User not allowed in this chatroom"

    # 이모티콘을 메시지처럼 채팅방에 추가
    message = Message(username=username, text=f"[Emoticon: {emoticon.name}]", chatroom=chatroom, timestamp=datetime.now())
    db.add(message)
    db.commit()

    # 세션이 닫히기 전에 필요한 데이터를 추출
    message_data = message.to_dict()

    return message_data, None


def upload_file(db:Session, filename: str, url: str, edited_by: List[str], chatroom: str):
    file = File(filename=filename, url=url, version=1, uploaded_at=datetime.now(), chatroom=chatroom, edited_by=','.join(edited_by))
    db.add(file)
    db.commit()

    # 세션이 닫히기 전에 필요한 데이터를 미리 추출
    file_data = file.to_dict()

    return file_data, None



def update_file_version(db:Session, filename: str, new_url: str, edited_by: List[str], chatroom: str):
    existing_files = db.query(File).filter(File.filename==filename, File.chatroom==chatroom).order_by(File.version.desc()).all()
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
    db.add(file)
    db.commit()

    # 세션이 닫히기 전에 필요한 데이터를 미리 추출
    file_data = file.to_dict()

    return file_data, None


def get_room_data(db:Session, chatroom: str):
    room = db.query(ChatRoom).filter_by(ChatRoom.name==chatroom).first()
    if room:
        messages = db.query(Message).filter_by(Message.chatroom==chatroom).all()
        emoticons = db.query(Emoticon).filter_by(Emoticon.chatroom==chatroom).all()
        files = db.query(File).filter_by(chatroom=chatroom).all()
        
        # Combine all data
        combined_data = messages + emoticons + files

        # Sort by the appropriate datetime attribute
        combined_data.sort(key=lambda x: x.timestamp if hasattr(x, 'timestamp') else x.uploaded_at)

        return combined_data, None
    raise PermissionError("Chatroom not found or access denied")
