from kobukidriver import Kobuki
import keyboard

kobuki_instance = Kobuki()

def move(left_velocity, right_velocity):
    botspeed = (left_velocity + right_velocity) / 2
    
    if left_velocity == right_velocity:
        botradius = 0
    else:
        botradius = (230 * (left_velocity + right_velocity)) / (2 * (right_velocity - left_velocity))

    cs = 0
    barr = bytearray([170, 85, 6, 1, 4])
    barr += int(botspeed).to_bytes(2, byteorder='little', signed=True)
    barr += int(botradius).to_bytes(2, byteorder='little', signed=True)
    
    for i in range(2, len(barr) - 1):
        cs = cs ^ barr[i]
    
    barr += cs.to_bytes(1, byteorder='big')
    Kobuki.seri.write(barr)

try:
    while True:
        if keyboard.is_pressed('up'):
            move(100, 100)
        elif keyboard.is_pressed('down'):
            move(-100, -100)
        elif keyboard.is_pressed('left'):
            move(0, 100)
        elif keyboard.is_pressed('right'):
            move(100, 0)
        else:
            move(0, 0)

except KeyboardInterrupt:
    move(0, 0)
    print("Manual control stopped.")
