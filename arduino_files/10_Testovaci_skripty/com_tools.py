"""Tools for PC<--->robohlava communication.
Communication protocol:

+-----------------------------------------------------------------------------+
|CMD| RX payload                         | TX payload                |CMDmnemo|
+-----------------------------------------------------------------------------+
| 1 | [CMD; MOT_NUM; STEPS_HB; STEPS_LB] | [CMD; OK]                 | SET    |
| 2 | [CMD; MOT_NUM]                     | [CMD; STEPS_HB; STEPS_LB] | READ   |
| 3 | [CMD; MOSFET_NUM; DUTY]            | [CMD]                     | MOSFET |
| 4 | [CMD]                              | [CMD; DONE]               | HOME?  |
| 5 | [CMD]                              | [CMD]                     | HOME   |
+-----------------------------------------------------------------------------+

where:

MOT_NUM = (1 - TILT; 2 - PAN);
STEPS = (TILT 0 - 320, PAN 0 - 195);
OK = (1 - MESSAGE OK; 0 - MESSAGE NOK)
MOSFET_NUM = (1 - 6); DUTY = (0 - 255)
HB = High Byte
LB = Low Byte

"""

import serial
import time
START_BYTE = 55
STOP_BYTE = 110

def error(string):
    print("[ERROR] " + string)

def info(string):
    print("[INFO] " + string)

class Arduino():
    START_BYTE = 55
    STOP_BYTE = 110
    def __init__(self, platform="windows"):
        """Define and initializate arduino Python comunication.
        """
        try:
            if platform == "windows":
                self.arduino = serial.Serial('COM3', 115200)  # Windows
            if platform == "linux":
                self.arduino = serial.Serial('/dev/ttyACM0', 115200)  # Linux
            info("initialization complete.")
        except:
            error("initialization arduino.")


    def moveX(self, angle):
        # TODO
        """Move in x axis.
        """
        # global START_BYTE, STOP_BYTE
        try:
            cmd = 1
            mot = 2
            payload = [cmd, mot] + self.angle2payload(angle)
            print("payload", payload)
            msg = (bytearray([START_BYTE, len(payload) + 3]) +
                    bytearray(payload) + bytearray([STOP_BYTE]))
            print("msg:", msg)
            self.arduino.write(msg)
            return_msg = list(self.arduino.read(16))
            while return_msg is None:
                return_msg = list(self.arduino.read(16))
            print("return msg: ", return_msg)
            info("message sent succesfully.")
        except:
            error("message sent. func: moveX()")


    def moveY(self, angle):
        """Move in y asix.
        """
        # global START_BYTE, STOP_BYTE
        cmd = 1
        mot = 1
        payload = [cmd, mot] + self.angle2payload(angle)
        msg = bytearray([START_BYTE, len(payload) + 3]) + bytearray(payload) + bytearray([STOP_BYTE])
        self.arduino.write(msg)


    def angle2payload(self, angle):
        """Convert angle to payload uint8 format.
        Payload = [hight byte, low byte]

        Argumets:
            angle - angle in degrease
        Return:
            payload_angle - [Hb, Lb]
        """

        if angle >= 256:
            return [1, angle-256]
        else:
            return [0, angle]


    def payload2angle(self, payload):
        """Convert payload uint8 format to angle .
        Payload = [hight byte, low byte]

        Argumets:
            payload_angle - [Hb, Lb]
        Return:
            angle - angle in degrease
        """
        if payload[0] == 0:
            return payload[1]
        else:
            return payload[1] + 256


def test():
    start_byte = 55
    stop_byte = 110

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

if __name__ == "__main__":
    test()
