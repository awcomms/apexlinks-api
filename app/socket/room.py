from flask_socketio import leave_room
from app import socket

@socket.on('leave')
def leave(data):
    leave_room