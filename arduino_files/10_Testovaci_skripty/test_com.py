
"""
Test code for communication with RH in python
"""
import numpy as np
import serial
import time
import com_tools as ct

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1);
time.sleep(10)

start_byte = 55
stop_byte = 110


payload = [3, 1, 255]

msg = bytearray([start_byte, len(payload) + 3]) + bytearray(payload) + bytearray([stop_byte])
print(msg)

ser.write(msg)
print(list(msg))
print(list(ser.read(16)))

time.sleep(10)
print(list(msg))
ser.write(msg)
print(list(ser.read(16)))

time.sleep(1)
print(list(msg))
ser.write(msg)
print(list(ser.read(16)))

while True:
    angle = int(input("input angle:"))
    cmd = 1
    mot = 1
    print("angle:",angle)
    angle_payload = ct.angle2payload(angle)
    print("angle_payload:", angle_payload)
    payload1part = [cmd, mot]
    payload = payload1part + angle_payload
    print(payload)

    msg = bytearray([start_byte, len(payload) + 3]) + bytearray(payload) + bytearray([stop_byte])
    print("msg:", msg)

    ser.write(msg)
    print(list(msg))
    print(list(ser.read(16)))

    time.sleep(10)
    print(list(msg))
    ser.write(msg)
    print(list(ser.read(16)))

    time.sleep(1)
    print(list(msg))
    ser.write(msg)
    print(list(ser.read(16)))

ser.close()
