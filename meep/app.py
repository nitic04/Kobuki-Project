import math

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import serial
import serial.tools.list_ports as lsports
import time

app = Flask(__name__)
socketio = SocketIO(app)

# from: https://github.com/jaxram/Kobukidriver/blob/main/build/lib/kobukidriver/Kobuki.py
def getKobukiPort():
    ports = lsports.comports()
    flag = 0
    print(
        ports
    )
    for kport, desc, hwid in sorted(ports):

        if (desc.find('USB Serial Port') != -1):
            print("kobuki is connected in the Following Port")
            print("{} {} [{}]".format(kport, desc, hwid))
            print(kport[0:4])
            return serial.Serial(port=kport[0:4], baudrate=115200)
        elif (desc.find('Kobuki') != -1):
            # print(kport,desc)
            print("kobuki is connected in the Following Port")
            print("{} {} [{}]".format(kport, desc, hwid))
            # print(kport)
            return serial.Serial(port=kport, baudrate=115200)
    else:
        raise Exception("Kobuki is not connected")

# Initialize serial connection, taken from kobuki driver code
seri = getKobukiPort()

@app.route('/')
def index():
    return send_from_directory('.', 'meep.html')


target_x = 0
target_y = 0
acceleration = 0.05 # x and y change per ms
@socketio.on('joystick_move')
def handle_joystick_move(data):
    x = data['x']
    y = data['y']
    y = max(min(y, 100), -100)
    x = max(min(x, 100), -100)
    global target_x
    global target_y
    target_x = x
    target_y = y

    joystick_move(x,y)

def joystick_move(x, y):

    wheelbase = 0.230 * 1000 # 230 mm
    if -20 < x < 20 and -20 < y < 20:
        # stop
        speed = 0
        radius = 0
    elif -50 < x < 50:
        # pure translation
        speed = y * 400/100 # 700 mm/s is the max speed of the robot, y is from -100 to 100
        radius = 0
    elif -50 < y < 50:
        # pure rotation
        speed = (x* 1.91986 /100) * wheelbase / 2 #  1.91986 rad/s is the max angular speed of the robot, x is from -100 to 100
        radius = 1 if x > 0 else -1

        speed *= -radius
    else:
        print("boop")
        # translation + rotation
        radius = math.atan(x / y)
        # normalize the radius
        # radius = ((math.pi / 2)/radius) * 1000
        radius = -math.copysign(200, radius)
        speed = y * 700/100 # 700 mm/s is the max speed of the robot, y is from -100 to 100
        if radius >= 0:
            # Speed * (Radius + b) / 2 ) / Radius, if Radius > 1
            speed = speed * (radius + wheelbase / 2) / (2 * radius)
        else:
            # Speed * (Radius - b / 2 ) / Radius, if Radius < -1
            speed = speed * (radius - wheelbase / 2) / (2 * radius)

    send_move_command(min(max(speed, -32768),32767), radius)

def send_move_command(botspeed, botradius):
    print(f'Sending move command with speed {botspeed} and radius {botradius}')
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
    
    
# def robot_loop():
#     current_x = 0
#     current_y = 0
#     last_update = 0
#     update_time = 5 # in ms

#     while True:
       # if int.from_bytes(seri.read(2), byteorder='little') == 333:
       #     __temp = seri.read(200)

        # now = time.time() * 1000
        # delta = now - last_update
        # if delta > update_time:
        #     if current_x != target_x:
        #         if current_x - target_x < acceleration*delta:
        #             current_x = target_x
        #         elif current_x < target_x:
        #             current_x += acceleration * delta
        #         else:
        #             current_x -= acceleration * delta
        #     if current_y != target_y:
        #         if current_y - target_y < acceleration*delta:
        #             current_y = target_y
        #         elif current_y < target_y:
        #             current_y += acceleration * delta
        #         else:
        #             current_y -= acceleration * delta

        # if current_x != target_x or current_y != target_y:
        #     joystick_move(current_x, current_y)

        # last_update = now



if __name__ == '__main__':
    import threading
    # threading.Thread(target=robot_loop).start()
    socketio.run(app, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)
