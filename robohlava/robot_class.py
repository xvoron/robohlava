"""
                    MOTOR_Y
                     100
                      |
                      |
MOTOR_X         0_____x_____195
                      |
                      |
                      0
"""

from robohlava.voice import Voice
import threading
import math
import time
from robohlava.arduino import Arduino
import robohlava.config as conf


class Robohlava():
    def __init__(self):
        self.width = conf.WIDTH
        self.height = conf.HEIGHT

        self.flag_voice = conf.flag_voice
        self.flag_arduino = conf.flag_arduino
        self.TIMER = 0
        self.actual_x, self.actual_y = conf.arduino_base.copy()
        if self.flag_voice:
            self.voice = Voice()
            # self.voice.completed.set()
        else:
            self.engine_voice = None
            self.voice = self.say
        if self.flag_arduino:
            self.arduino = Arduino()
        else:
            self.arduino = None

    def calculate_turn_coordinates(self, centroid_to_arduino):
        if centroid_to_arduino is not None:
            delta_x = centroid_to_arduino[0] - self.width/2
            delta_y = centroid_to_arduino[1] - self.height/2
            delta = math.sqrt(delta_x**2 + delta_y**2)
            if delta < 50:
                pass
            else:
                if self.TIMER > conf.arduino_padding:
                    if delta_x > 50:
                        self.actual_x += conf.arduino_x_constant + abs(int(delta_x * conf.arduino_x_multiplicator))      # -int(delta_x * 0.05)
                    if delta_x < -50:
                        self.actual_x -= conf.arduino_x_constant + abs(int(delta_x * conf.arduino_x_multiplicator))     #-int(delta_x * 0.05)
                    if delta_y > 50:
                        self.actual_y -= conf.arduino_y_constant + abs(int(delta_y * conf.arduino_y_multiplicator))   # -int(delta_y * 0.08)
                    if delta_y < -50:
                        self.actual_y += conf.arduino_y_constant + abs(int(delta_y * conf.arduino_y_multiplicator))    # -int(delta_y * 0.01)
                    self.turn(self.actual_x, self.actual_y)
                    self.TIMER = 0
        self.TIMER += 1

    def say_with_thread(self, text):
        """
        queue = [].append(text)
        while queue:
            if self.voice.completed.is_set():
                self.voice.completed.clear()
                if len(queue):
                    self.voice.say(queue.pop(0))
            else:
                continue
        """
        if self.voice.completed.is_set():
            self.voice.completed.clear()
            if text is not None:
                self.voice.say(text)

    def do_voice_process_queue(self, q):
            while not q.empty():
                voice = threading.Thread(target=self.voice, args=(q.get(), self.engine_voice))
                voice.start()

    def say(self, text):
        if self.flag_voice:
            self.voice.say(text)
        else:
            print("[INFO] Text to voice: \n {0}".format(text))

    def _say(self, text):
            if self.flag_voice:
                voice = threading.Thread(target=self.voice, args=(text, self.engine_voice))
                voice.start()
            else:
                print("Text to voice: \n {0}".format(text))

    def turn_tread(self, x, y):
        if self.flag_arduino:
            self.actual_x = x
            self.actual_y = y
            self.arduino.move(1, self.actual_y)
            time.sleep(0.5)
            self.arduino.move(2, self.actual_x)
        else:
            self.actual_x = x
            self.actual_y = y
            print("arduino data send: x-> {0} , y-> {1}".format(self.actual_x,
                                                                self.actual_y))

    def turn(self, x, y):
        thread = threading.Thread(target=self.turn_tread, args=(x, y))
        thread.start()

    def emotions_yes_no(self, emotion="yes"):
        if emotion == "yes":
            pass

    def update(self, voice_text, turn):
        pass

    def terminate(self):
            time.sleep(2)
            self.turn(conf.arduino_base[0], conf.arduino_base[1])
            print("[TERM] Turn to base position")
            time.sleep(2)
            print("[TERM] Terminate Arduino, Voice started")
            if self.flag_arduino:
                self.arduino.terminate()
            if self.flag_voice:
                self.voice.terminate()


if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))

else:
    print("Modul  | {0} | ---> imported".format(__name__))
