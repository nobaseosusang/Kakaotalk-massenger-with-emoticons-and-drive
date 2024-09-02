from flask import Flask, request, jsonify, session, g
from flask_cors import CORS


from src.database.controller import (
    register_user, authenticate_user, create_chatroom, send_message, get_messages, 
    add_emoticon, get_emoticons, upload_file, update_file_version, get_room_data,send_emoticon
)
from config import config
from src.database.database import get_db




def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = config.SECRET_KEY

    # Database 객체 생성

    @app.before_request
    def before_request():
        g.db_session = get_db()

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
    
    
    user_data, error = register_user(db=g.db_session, username=data['username'], password=data['password'])
    if error:
        return jsonify({'status': 'Error', 'message': error}), 409  # 409 Conflict 상태 코드 반환
    
    return jsonify({'status': 'User registered', 'user': user_data['username']})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    if authenticate_user(db=g.db_session, username=data['username'], password=data['password']):
        session['username'] = data['username']
        print(f"Username {data['username']} stored in session")
        return jsonify({'status': 'Login successful','username':session['username']})
    
    print("Login failed: Invalid credentials")
    return jsonify({'status': 'Invalid credentials'}), 401

@app.route('/check_username', methods=['POST'])
def checkon():
    username = session.get('username')
    return jsonify({'username' : username})

    

@app.route('/create_chatroom', methods=['POST'])
def create_chatroom_route():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    chatroom_data, error = create_chatroom(db=g.db_session, name=data['name'], allowed_users=data['allowed_users'])
    if error:
        return jsonify({'status': 'Error', 'message': error}), 409  
    
    return jsonify({'status': 'Chatroom created', 'chatroom': chatroom_data['name']})



@app.route('/send_message', methods=['POST'])
def send_message_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    username = session.get('username')
    message_data, error = send_message(db=g.db_session, username=username, text=data['text'], chatroom=data['chatroom'])
    
    if error:
        return jsonify({'status': 'Error', 'message': error}), 403
    
    return jsonify({'status': 'Message sent', 'message': message_data})


@app.route('/get_messages', methods=['GET'])
def get_messages_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    
    chatroom = request.args.get('chatroom')
    if not chatroom:
        return jsonify({'status': 'Chatroom name is required'}), 400
    
    messages, error = get_messages(db=g.db_session, chatroom=chatroom)
    if error:
        return jsonify({'status': 'Error', 'message': error}), 403
    
    # 각 메시지를 딕셔너리로 변환
    messages_data = [message.to_dict() for message in messages]
    
    return jsonify(messages_data)


@app.route('/add_emoticon', methods=['POST'])
def add_emoticon_route():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    emoticon_data, error = add_emoticon(db=g.db_session, **data)
    if error:
        return jsonify({'status': 'Error', 'message': error}), 409  # 409 Conflict 상태 코드 반환
    
    return jsonify({'status': 'Emoticon added', 'emoticon': emoticon_data})

@app.route('/get_emoticons', methods=['GET'])
def get_emoticons_route():
    category = request.args.get('category')
    
    emoticons, error = get_emoticons(db=g.db_session, category=category)
    if error:
        return jsonify({'status': 'Error', 'message': error}), 400

    # 이모티콘 리스트를 딕셔너리로 변환하여 반환
    emoticons_data = [emoticon.to_dict() for emoticon in emoticons]
    return jsonify(emoticons_data)

@app.route('/send_emoticon', methods=['POST'])
def send_emoticon_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401

    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400

    username = session.get('username')
    emoticon_id = data.get('emoticon_id')
    chatroom = data.get('chatroom')

    if not emoticon_id or not chatroom:
        return jsonify({'status': 'Missing emoticon ID or chatroom'}), 400

    result, error = send_emoticon(db=g.db_session, username=username, emoticon_id=emoticon_id, chatroom=chatroom)

    if error:
        return jsonify({'status': 'Error', 'message': error}), 403

    return jsonify({'status': 'Emoticon sent', 'emoticon': result})


@app.route('/upload_file', methods=['POST'])
def upload_file_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    file, error = upload_file(db=g.db_session, filename=data['filename'], url=data['url'], edited_by=data['edited_by'], chatroom=data['chatroom'])
    if error:
        return jsonify({'status': 'Error', 'message': error}), 409  # 409 Conflict 상태 코드 반환
    
    return jsonify({'status': 'File uploaded', 'file': file})


@app.route('/update_file_version', methods=['POST'])
def update_file_version_route():
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'Invalid input, JSON data expected'}), 400
    
    updated_file, error = update_file_version(db=g.db_session, filename=data['filename'], new_url=data['new_url'], edited_by=data['edited_by'], chatroom=data['chatroom'])
    if error:
        return jsonify({'status': 'Error', 'message': error}), 404  # 404 Not Found 상태 코드 반환
    
    return jsonify({'status': 'File updated', 'file': updated_file})


@app.route('/get_room_data', methods=['GET'])
def get_room_data_route():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    
    chatroom = request.args.get('chatroom')
    if not chatroom:
        return jsonify({'status': 'Chatroom name is required'}), 400
    
    room_data, error = get_room_data(db=g.db_session, chatroom=chatroom)
    if error:
        return jsonify({'status': 'Error', 'message': error}), 403
    
    # 각 객체를 to_dict() 메서드를 통해 딕셔너리로 변환
    room_data_dicts = [item.to_dict() for item in room_data]
    
    return jsonify(room_data_dicts)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=13242)
