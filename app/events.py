from flask import session
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
import app.helpers as h
import app.constants as c

ROOMS = {}

@socketio.on("connect")
def handle_connect():
    if "USER" in session:
        print("Client connected: ", session["USERNAME"])
    else:
        print("Client connected!")


@socketio.on("disconnect")
def handle_disconnect():
    if "USER" in session:
        if session["USER"] in ROOMS:
            ROOMS.pop(session["USER"])
        print("Client disconnected:", session["USERNAME"])
    else:
        print("Client disconnected!")

@socketio.on("join_room")
def handle_join(user, recipient):
    room = f"{user}{recipient}"
    join_room(room)
    ROOMS[session['USER']] = room
    print(f"{session['USERNAME']} joined room {room}")

@socketio.on("leave_room")
def handle_leave(user, recipient):
    room = f"{user}{recipient}"
    leave_room(room)
    ROOMS.pop(session["USER"])
    print(f"{session['USERNAME']} left room {room}")

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
        room = f"{msg.sender.id}{recipient}"
        room_two = f"{recipient}{msg.sender.id}"
        
        emit("private_message", {"sender": msg.sender.id,
                                 "name": msg.sender.first,
                                "message": msg.message,
                                "time": h.format_timestamp(msg.timestamp)},
                                to=room)
        
        if int(recipient) in ROOMS and ROOMS[int(recipient)] == room_two:
            emit("private_message", {"sender": msg.sender.id,
                                "name": msg.sender.first,
                                "message": msg.message,
                                "time": h.format_timestamp(msg.timestamp)},
                                to=room_two)
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