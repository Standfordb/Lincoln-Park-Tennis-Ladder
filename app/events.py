from flask import session, request
from flask_socketio import emit
from app.extensions import socketio
import app.helpers as h
import app.constants as c

SID = {}

@socketio.on("connect")
def handle_connect():
    if "USER" in session:
        SID[session["USER"]] = request.sid
        print("Client connected: ", session["USERNAME"])
    else:
        print("Client connected!")


@socketio.on("disconnect")
def handle_connect():
    if "USER" in session:
        SID[session["USER"]] = None
        print("Client disconnected: ", session["USERNAME"])
    else:
        print("Client disconnected!")


@socketio.on("chat_message")
def handle_chat_message(message):
    if not "USER" in session:
        emit("chat_message", {"sender": "Error",
                              "message": "Must be logged in to chat."})
    elif h.blank_message(message):
        pass
    else:
        msg = h.save_broadcast_message(message)
        emit("chat_message", {"sender": msg.sender.first + " " + msg.sender.last,
                            "message": msg.message,
                            "time": h.format_timestamp(msg.timestamp)},
                            broadcast=True)


@socketio.on("private_message")
def handle_private_message(message, recipient):
    if h.blank_message(message):
        pass
    else:
        msg = h.save_private_message(message, recipient)
        emit("private_message", {"sender": msg.sender.id,
                                 "name": msg.sender.first,
                                "message": msg.message,
                                "time": h.format_timestamp(msg.timestamp)},
                                to=SID[session["USER"]])
        if int(recipient) in SID:
            emit("private_message", {"sender": msg.sender.id,
                                 "name": msg.sender.first,
                                "message": msg.message,
                                "time": h.format_timestamp(msg.timestamp)},
                                to=SID[int(recipient)])
