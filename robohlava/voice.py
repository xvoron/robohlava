"""
Modul for utilities and tool in project robohlava

"""
import pyttsx3
import queue
from threading import Thread
from multiprocessing import Process


class Voice:
    def __init__(self):
        """Voice engine initialization
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_csCZ_Jakub')
        self.engine.setProperty('rate', 200)  # setting up new voice rate
        self.t_children = Thread()
        self.t_parent = Thread()
        self.q = queue.Queue()

    def say_engine(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def say_thread(self):
        while not self.q.empty():
            if not self.t_children.is_alive():
                self.t_children = Thread(target=self.say_engine,
                                         args=(self.q.get(),))
                self.t_children.start()

    def say(self, text):
        """
        Speech function.

        Take a text string and say it with pyttsx3 engine.
        :param text:
        :return:
        """
        self.q.put(text)
        if not self.t_parent.is_alive():
            self.t_parent = Thread(target=self.say_thread)
            self.t_parent.start()

    def _say(self, text):
        """
        Speech function.

        Take a text string and say it with pyttsx3 engine.
        :param text:
        :return:
        """
        self.q.put(text)
        if not self.t_parent.is_alive():
            self.t_parent = Process(target=self.say_thread)
            self.t_parent.start()

    def terminate(self):
        self.engine.stop()
        print("[TERM] Voice is stoped")

    def kill_running_voice(self):
        self.t_children.join()
        self.t_parent.join()

    def _kill_running_voice(self):
        self.t_parent.terminate()


if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))

else:
    print("Modul  | {0} | ---> imported".format(__name__))
