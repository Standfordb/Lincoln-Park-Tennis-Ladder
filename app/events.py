from app.extensions import socketio
import app.helpers as h

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("user_connect")
def handle_user_connect():
    user = h.get_user()
    print(f"User {user.username} has joined!")