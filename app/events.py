from flask import session, request, flash
from flask_socketio import emit
from app.extensions import socketio
from app import routes as r
import app.helpers as h
import app.constants as c

SID = {}

@socketio.on("connect")
def handle_connect():
    if "USER" in session:
        SID[session["USER"]] = request.sid
        print("Client connected: ", session["USERNAME"])
        print("SID =", SID)
    else:
        print("Client connected!")


@socketio.on("disconnect")
def handle_connect():
    if "USER" in session:
        SID.pop(session["USER"])
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
        notification = h.Notification.query.filter_by(user_id=recipient, originator_id=msg.sender.id, type=c.MESSAGE).first()
        
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
        else:
            if not notification:
                h.create_notification(recipient, msg.sender.id, c.MESSAGE)

@socketio.on("handle_challenge")
def handle_challenge(msg, challenger_id, notification_id):
    outcome = h.handle_challenge(msg, challenger_id, notification_id)
    user = h.get_user()
    count = len(user.notifications)
    if outcome == False:
        emit("error_open_challenge", {"id": notification_id,
                                    "msg": "(You already have an open challenge.)"})
    else:
        emit("update_notifications", {"id": notification_id,
                                    "count": count})
    

@socketio.on("remove_notification")
def remove_notification(id):
    h.remove_notification(id)
    user = h.get_user()
    count = len(user.notifications)
    emit("update_notifications", {"id": id,
                                "count": count})