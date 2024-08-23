# RED TEAM LED SETUP
import serial

seri = serial.Serial(port='COM3', baudrate=115200, timeout=2)

led1 = bytearray([170,85,4,12,2,0,1,11])
led2 = bytearray([170,85,4,12,2,0,4,14])
seri.write(led1)
seri.write(led2)