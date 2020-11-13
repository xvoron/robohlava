"""
Test code for communication with RH in python
"""

import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1);
time.sleep(10)

start_byte = 55
stop_byte = 110


payload = [2, 1]

msg = bytearray([start_byte, len(payload) + 3]) + bytearray(payload) + bytearray([stop_byte])

ser.write(msg)
print("msg:", list(msg))
print("msg read:",list(ser.read(16)))

time.sleep(10)
print("msg:", list(msg))
ser.write(msg)
print("msg read:",list(ser.read(16)))

time.sleep(1)
print("msg:", list(msg))
ser.write(msg)
print("msg read:",list(ser.read(16)))

ser.close()
