import os
from flask import Flask, request, jsonify, session, g
from src.database.controller import (
    register_user, authenticate_user, create_chatroom, send_message, get_messages, 
    add_emoticon, get_emoticons, upload_file, update_file_version, get_room_data
)
from src.database.database import Database
from src.database.models import Base
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.secret_key = os.urandom(24)

    # Database 객체 생성
    database = Database()

    # 데이터베이스 엔진에 메타데이터를 바인딩하여 테이블 생성
    with app.app_context():
        Base.metadata.bind = database.engine  # 명시적으로 엔진을 바인딩
        Base.metadata.create_all()  # 테이블 생성

    @app.before_request
    def before_request():
        g.db_session = database.get_session()

    return app

app = create_app()

@app.teardown_appcontext
def teardown_db(exception):
    db_session = g.pop('db_session', None)
    if db_session is not None:
        db_session.close()

# 라우트 정의

@app.route('/status')
def status():
    return jsonify({'status': 'ok'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    user_data, error = register_user(data['username'], data['password'])
    if error:
        return jsonify({'status': 'Error', 'message': error}), 409  # 409 Conflict 상태 코드 반환
    
    return jsonify({'status': 'User registered', 'user': user_data['username']})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    if authenticate_user(data['username'], data['password']):
        session['username'] = data['username']
        return jsonify({'status': 'Login successful'})
    return jsonify({'status': 'Invalid credentials'}), 401

@app.route('/create_chatroom', methods=['POST'])
def create_chatroom_route():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    chatroom = create_chatroom(data['name'], data['allowed_users'])
    return jsonify({'status': 'Chatroom created', 'chatroom': chatroom.name})

@app.route('/send_message', methods=['POST'])
def send_message_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    try:
        message = send_message(session['username'], data['text'], data['chatroom'])
        return jsonify({'status': 'Message sent', 'message': message.dict()})
    except PermissionError as e:
        return jsonify({'status': str(e)}), 403

@app.route('/get_messages', methods=['GET'])
def get_messages_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    chatroom = request.args.get('chatroom')
    try:
        if not chatroom:
            return jsonify({'status': 'Chatroom name is required'}), 400
    
        messages = get_messages(chatroom)
        return jsonify([message.dict() for message in messages])
    except PermissionError as e:
        return jsonify({'status': str(e)}), 403

@app.route('/add_emoticon', methods=['POST'])
def add_emoticon_route():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    emoticon = add_emoticon(data['name'], data['url'], data['size'], data['animated'], data['category'], data['chatroom'])
    return jsonify({'status': 'Emoticon added', 'emoticon': emoticon.dict()})

@app.route('/get_emoticons', methods=['GET'])
def get_emoticons_route():
    category = request.args.get('category')
    if not category:
        return jsonify({'status': 'Category name is required'}), 400
    
    emoticons = get_emoticons(category)
    return jsonify([emoticon.dict() for emoticon in emoticons])

@app.route('/upload_file', methods=['POST'])
def upload_file_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    file = upload_file(data['filename'], data['url'], data['edited_by'], data['chatroom'])
    return jsonify({'status': 'File uploaded', 'file': file.dict()})

@app.route('/update_file_version', methods=['POST'])
def update_file_version_route():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    updated_file = update_file_version(data['filename'], data['new_url'], data['edited_by'], data['chatroom'])
    if updated_file:
        return jsonify({'status': 'File updated', 'file': updated_file.dict()})
    else:
        return jsonify({'status': 'File not found'}), 404

@app.route('/get_room_data', methods=['GET'])
def get_room_data_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    chatroom = request.args.get('chatroom')
    if not chatroom:
        return jsonify({'status': 'Chatroom name is required'}), 400

    try:
        room_data = get_room_data(chatroom)
        return jsonify([item.dict() for item in room_data])
    except PermissionError as e:
        return jsonify({'status': str(e)}), 403


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=13242)
