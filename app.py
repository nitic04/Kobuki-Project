from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import serial
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize serial connection, taken from kubuki driver code
seri = serial.Serial(port='COM3', baudrate=115200, timeout=2)

def move(left_velocity, right_velocity):
    botspeed = (left_velocity + right_velocity) / 2
    botradius = (230 * (left_velocity + right_velocity)) / (2 * (right_velocity - left_velocity)) if left_velocity != right_velocity else 0
    
    cs = 0
    barr = bytearray([170, 85, 6, 1, 4])
    barr += int(botspeed).to_bytes(2, byteorder='little', signed=True)
    barr += int(botradius).to_bytes(2, byteorder='little', signed=True)
    print(botspeed, botradius)
    
    for i in range(2, len(barr) - 1):
        cs = cs ^ barr[i]
    
    barr += cs.to_bytes(1, byteorder='big')
    seri.write(barr)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def handle_movement(message):
    if message == 'UP':
        move(100, 100)
    elif message == 'DOWN':
        move(-100, -100)
    elif message == 'LEFT':
        move(0, 200)
    elif message == 'RIGHT':
        move(200, 0)
    elif message == 'STOP':
        move(0, 0)

@socketio.on('message')
def handle_message(message):
    print(f'Received message: {message}')
    handle_movement(message)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
