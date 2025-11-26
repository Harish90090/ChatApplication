from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, join_room
from flask_cors import CORS
from backend.config import config
from backend.database import init_db
from backend.models.user import User
from backend.models.private_chat import PrivateChat
from backend.models.group_chat import GroupChat

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initializeing SocketIO with CORS
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True)

#Enableing CORS for all routes
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE"],
     allow_headers=["Content-Type", "Authorization"])

# Initialize database
print("Initializing database.")
try:
    init_db()
    print(" Database initialization complete!")
except Exception as e:
    print(f" Database initialization failed: {e}")
    exit(1)

#AUTH ROUTES
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
       #VALIDATION
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
       #CREATING THE USER
        user_id, error = User.create(username, email, password)
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'User created successfully', 
            'user_id': user_id
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.verify_password(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            print(f" User {username} logged in successfully")
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        print(f"User {username} logged out")
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        if 'user_id' in session:
            user = User.get_by_id(session['user_id'])
            if user:
                return jsonify({
                    'authenticated': True,
                    'user': user
                }), 200
        
        return jsonify({'authenticated': False}), 401
        
    except Exception as e:
        print(f"Auth check error: {e}")
        return jsonify({'authenticated': False}), 401

#user routess

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users except current user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        users = User.get_all(exclude_user_id=session['user_id'])
        return jsonify(users), 200
        
    except Exception as e:
        print(f" Get users error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

#Private chat routes

@app.route('/api/private/start-chat/<int:other_user_id>', methods=['POST'])
def start_private_chat(other_user_id):
    """Start or get existing private chat"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        chat = PrivateChat.get_or_create(session['user_id'], other_user_id)
        if chat:
            return jsonify(chat), 200
        else:
            return jsonify({'error': 'Failed to create chat'}), 500
            
    except Exception as e:
        print(f"Start private chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/private/send-message', methods=['POST'])
def send_private_message():
    """Send private message"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        
        if not receiver_id or not content:
            return jsonify({'error': 'Receiver ID and content are required'}), 400
        
        message = PrivateChat.send_message(session['user_id'], receiver_id, content)
        if message:
            return jsonify(message), 201
        else:
            return jsonify({'error': 'Failed to send message'}), 500
            
    except Exception as e:
        print(f"Send private message error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/private/messages/<int:other_user_id>', methods=['GET'])
def get_private_messages(other_user_id):
    """Get private messages between users"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        messages = PrivateChat.get_messages(session['user_id'], other_user_id)
        return jsonify(messages), 200
        
    except Exception as e:
        print(f"Get private messages error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/private/chats', methods=['GET'])
def get_private_chats():
    """Get all private chats for user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        chats = PrivateChat.get_user_chats(session['user_id'])
        return jsonify(chats), 200
        
    except Exception as e:
        print(f"Get private chats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

#GroupChat routes

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all groups"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        groups = GroupChat.get_all_groups()
        return jsonify(groups), 200
        
    except Exception as e:
        print(f" Get groups error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/groups/my', methods=['GET'])
def get_my_groups():
    """Get user's groups"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        groups = GroupChat.get_user_groups(session['user_id'])
        return jsonify(groups), 200
        
    except Exception as e:
        print(f"Get my groups error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/groups/create', methods=['POST'])
def create_group():
    """Create new group"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'error': 'Group name is required'}), 400
        
        group_id = GroupChat.create(name, description, session['user_id'])
        if group_id:
            return jsonify({
                'message': 'Group created successfully', 
                'group_id': group_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create group'}), 500
            
    except Exception as e:
        print(f" Create group error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/groups/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    """Join a group"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        success = GroupChat.add_member(group_id, session['user_id'])
        if success:
            return jsonify({'message': 'Joined group successfully'}), 200
        else:
            return jsonify({'message': 'Already a member'}), 200
            
    except Exception as e:
        print(f" Join group error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/groups/<int:group_id>/send-message', methods=['POST'])
def send_group_message(group_id):
    """Send group message"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        message = GroupChat.send_message(group_id, session['user_id'], content)
        if message:
            return jsonify(message), 201
        else:
            return jsonify({'error': 'Failed to send message'}), 500
            
    except Exception as e:
        print(f"Send group message error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/groups/<int:group_id>/messages', methods=['GET'])
def get_group_messages(group_id):
    """Get group messages"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        messages = GroupChat.get_messages(group_id)
        return jsonify(messages), 200
        
    except Exception as e:
        print(f"Get group messages error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/groups/<int:group_id>/members', methods=['GET'])
def get_group_members(group_id):
    """Get group members"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        members = GroupChat.get_group_members(group_id)
        return jsonify(members), 200
        
    except Exception as e:
        print(f"Get group members error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

#socket.io event handler s

@socketio.on('connect')
def handle_connect():
    #handleing socket connection
    if 'user_id' in session:
        print(f"User {session['username']} connected (SID: {request.sid})")
    else:
        print(f"Unauthenticated user connected (SID: {request.sid})")

@socketio.on('disconnect')
def handle_disconnect():
    #which handle socket disconnection
    if 'user_id' in session:
        print(f"User {session['username']} disconnected (SID: {request.sid})")
    else:
        print(f"Unauthenticated user disconnected (SID: {request.sid})")

@socketio.on('join_private_chat')
def handle_join_private_chat(data):
   #join private chat room
    if 'user_id' not in session:
        print("Unauthenticated user tried to join private chat")
        return
    
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        print("No other_user_id provided for private chat")
        return
    
    room = f"private_{min(session['user_id'], other_user_id)}_{max(session['user_id'], other_user_id)}"
    join_room(room)
    print(f"User {session['username']} joined private chat room: {room}")

@socketio.on('join_group_chat')
def handle_join_group_chat(data):
    """Join group chat room"""
    if 'user_id' not in session:
        print("Unauthenticated user tried to join group chat")
        return
    
    group_id = data.get('group_id')
    if not group_id:
        print(" No group_id provided for group chat")
        return
    
    room = f"group_{group_id}"
    join_room(room)
    print(f"User {session['username']} joined group room: {room}")

@socketio.on('send_private_message')
def handle_send_private_message(data):
    """Handle sending private message via socket"""
    if 'user_id' not in session:
        print("Unauthenticated user tried to send private message")
        return
    
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    
    if not receiver_id or not content:
        print("Invalid private message data")
        return
    
    print(f"User {session['username']} sending private message to user {receiver_id}: {content}")
    
    # Save message to database
    message = PrivateChat.send_message(session['user_id'], receiver_id, content)
    
    if message:
        # Broadcast to both users in the private chat room
        room = f"private_{min(session['user_id'], receiver_id)}_{max(session['user_id'], receiver_id)}"
        print(f"Broadcasting private message to room: {room}")
        socketio.emit('receive_private_message', message, room=room)
        print(f" Private message sent and broadcast successfully")
    else:
        print("Failed to save private message to database")

@socketio.on('send_group_message')
def handle_send_group_message(data):
    """Handle sending group message via socket"""
    if 'user_id' not in session:
        print("Unauthenticated user tried to send group message")
        return
    
    group_id = data.get('group_id')
    content = data.get('content', '').strip()
    
    if not group_id or not content:
        print("Invalid group message data")
        return
    
    print(f"User {session['username']} sending group message to group {group_id}: {content}")
    
    # Save message to database
    message = GroupChat.send_message(group_id, session['user_id'], content)
    
    if message:
        # Broadcast to all users in the group room
        room = f"group_{group_id}"
        print(f"Broadcasting group message to room: {room}")
        socketio.emit('receive_group_message', message, room=room)
        print(f" Group message sent and broadcast successfully")
    else:
        print(" Failed to save group message to database")

#error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

#to start the backend 

if __name__ == '__main__':
    socketio.run(app)
