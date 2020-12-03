"""Arduino module

Tools for PC<--->robohlava communication.
Communication protocol:

[START_BYTE, msg_length, RX payload, STOP_BYTE]
[START_BYTE, msg_length, TX payload, STOP_BYTE]
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
import robohlava.config as conf

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
                self.arduino = serial.Serial(conf.arduino_com_port, 115200, timeout=0)  # Windows
            if platform == "linux":
                self.arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=0)  # Linux
            info("initialization complete.")
        except:
            error("initialization arduino.")
        self.calib_done = False

    def move(self, mot: int, angle: int):
        """Move RH.

        input:
            mot:int     - {1,2}, where 1 is Y-axis motor and 2 is X-axis.
            angle:int   - angle in degrees.

        return:
            TODO
            none

        """
        try:
            cmd = 1
            payload = [cmd, mot] + self.angle2payload(angle)
            # print("payload", payload)
            msg = (bytearray([START_BYTE, len(payload) + 3]) +
                   bytearray(payload) + bytearray([STOP_BYTE]))
            # print("msg:", msg)
            self.arduino.write(msg)
            return_msg = list(self.arduino.read(16).decode())
            self.arduino.flush()
            # print("[DEBUG] return message MOVE: ", return_msg)
            # return_msg = list(self.arduino.read(16))
            # while return_msg is None:
            #     return_msg = list(self.arduino.read(16))
            # print("return msg: ", return_msg)
            # info("message sent succesfully.")
        except:
            error("message sent. func: moveX()")

    def move_synch(self, angle1: int, angle2: int):
        """Move RH.

        input:
            mot:int     - {1,2}, where 1 is Y-axis motor and 2 is X-axis.
            angle:int   - angle in degrees.

        return:
            TODO
            none

        """
        try:
            cmd = 1
            payload1 = [cmd, 1] + self.angle2payload(angle1)
            payload2 = [cmd, 2] + self.angle2payload(angle2)
            print("payload1", payload1)
            msg = (bytearray([START_BYTE, len(payload1) + 3]) +
                   bytearray(payload1) + bytearray([STOP_BYTE]))
            msg += (bytearray([START_BYTE, len(payload2) + 3]) +
                    bytearray(payload2) + bytearray([STOP_BYTE]))
            print("msg:", msg)
            self.arduino.write(msg)
            # return_msg = list(self.arduino.read(16))
            # print("[DEBUG] return message MOVE: ", return_msg)
            # return_msg = list(self.arduino.read(16))
            # while return_msg is None:
            #     return_msg = list(self.arduino.read(16))
            # print("return msg: ", return_msg)
            info("message sent succesfully.")
        except:
            error("message sent. func: moveX()")

    def read_position(self, mot: int):
        # TODO
        """Read a motor position.

        input:
            mot:int     - {1,2}, where 1:Y and 2:X.
        return:
            angle:int   - angle in degrees.
        """
        cmd = 2
        payload = [cmd, mot]
        msg = bytearray([START_BYTE, len(payload) + 3]) + bytearray(payload) + bytearray([STOP_BYTE])
        self.arduino.write(msg)
        return_msg = list(self.arduino.read(16).decode())
        print("[DEBUG] return message READ: ", return_msg())
        i = 0
        while return_msg is None or i < 100:
            return_msg = list(self.arduino.read(16))
            i += 1
        print("[DEBUG] READ after while: ", return_msg)

    def calibration(self):
        # TODO
        """Doing calibration of 2 motors.

        input: none

        return: none
            calib_done:bool     - {True, False} state calibration.
        """
        payload = [5]
        msg: bytearray = bytearray([START_BYTE, len(payload) + 3]) + bytearray(payload) + bytearray([STOP_BYTE])
        print(msg)
        self.arduino.write(msg)
        print(list(self.arduino.read(16)))
        time.sleep(10)
        payload = [4]
        msg: bytearray = bytearray([START_BYTE, len(payload) + 3]) + bytearray(payload) + bytearray([STOP_BYTE])
        self.arduino.write(msg)
        return_msg = list(self.arduino.read(16))
        print("[INFO] return msg: {}".format(return_msg))
        # while True:
        #     if return_msg is not None:
        #         print(return_msg)
        #     return_msg = list(self.arduino.read(16))

    def angle2payload(self, angle):
        """Convert angle to payload uint8 format.
        Payload = [high byte, low byte]

        Argumets:
            angle - angle in degrease
        Return:
            payload_angle - [Hb, Lb]
        """

        if angle >= 256:
            return [1, angle - 256]
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

    def terminate(self):
        self.arduino.close()
        print("[TERM] Arduino is closed")




if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))

    model = Arduino()
    time.sleep(30)
    i = 0
    while True:

        time.sleep(0.5)
        i += 5
        if i > 100:
            break

    model.terminate()

else:
    print("Modul  | {0} | ---> imported".format(__name__))
