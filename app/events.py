from flask import session
from flask_socketio import emit
from app.extensions import socketio
import app.helpers as h

@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("chat_message")
def handle_chat_message(message):
    if not "USER" in session:
        emit("chat_message", {"sender": "Error",
                              "message": "Must be logged in to chat."})
        return
    elif h.blank_message(message):
        emit("chat_message", {"sender": "Error",
                              "message": "Chat message cannot be blank."})
    else:
        msg = h.save_message(message)
        emit("chat_message", {"sender": msg.sender.first + " " + msg.sender.last,
                            "message": msg.message,
                            "date": str(msg.timestamp)},
                            broadcast=True)
    
