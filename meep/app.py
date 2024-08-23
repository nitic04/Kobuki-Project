from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import serial

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize serial connection, taken from kobuki driver code
seri = serial.Serial(port='COM3', baudrate=115200, timeout=2)

def move(left_velocity, right_velocity):
    # 1: base control
    # 3: sound
    # 4: sound sequence


    # Calculate average speed of the robot
    botspeed = (left_velocity + right_velocity) / 2

    # Calculate turning radius of robot
    botradius = (230 * (left_velocity + right_velocity)) / (2 * (right_velocity - left_velocity)) if left_velocity != right_velocity else 0
    
    # Initializing cheksum which is used for error-checking
    cs = 0

    # Byte array that communicates with robot
    barr = bytearray([170, 85, 6, 1, 4])
    # 170: 0xAA -> header 0
    # 85: 0x55 -> header 1
    # 6: 0x06 in hex -> length
    # 1: 0x01 in hex -> payload(header, length, data)
    # 4: 0x04 in hex -> checksum

    # Adds speed and radius to byte array 
    barr += int(botspeed).to_bytes(2, byteorder='little', signed=True)
    barr += int(botradius).to_bytes(2, byteorder='little', signed=True)
    
    # Calculates checksum and adds it to the byte array
    for i in range(2, len(barr) - 1):
        cs = cs ^ barr[i]
    
    barr += cs.to_bytes(1, byteorder='big')

    # Sends the data via the serial port
    seri.write(barr)

@app.route('/')
def index():
    return send_from_directory('.', 'meep.html')

@socketio.on('joystick_move')
def handle_joystick_move(data):
    print(f'Received message: {data}')

    angle = data['botradius']
    speed = data['botspeed']

    if 0 < angle < 90 or 270 < angle < 360:
        move(4*speed, 0)
    elif 91 < angle < 180 or 181 < angle < 269:
        move(0, 4*speed)

    if 0 < angle < 239 or 291 < angle < 360:
        move(100+speed, 100+speed)
    elif 240 < angle < 290:
        move(-(100+speed), -(100+speed))
    
    if speed == 0 and angle == 0:
        move(0, 0)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
