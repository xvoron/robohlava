"""
Modul for utilities and tool in project robohlava

"""
import pyttsx3
import queue
from threading import Thread


class Voice:
    def __init__(self):
        """Voice engine initialization
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft'
                                         '\Speech\Voices\Tokens\MSTTS_V110_csCZ_Jakub')
        self.engine.setProperty('rate', 130)  # setting up new voice rate
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

    def terminate(self):
        self.engine.stop()


# Threading Class
class Threader(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.start()

    def run(self):
        tts_engine = pyttsx3.init()

        engine = pyttsx3.init()
        engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft'
                                    '\Speech\Voices\Tokens\MSTTS_V110_csCZ_Jakub')
        engine.setProperty('rate', 130)  # setting up new voice rate
        tts_engine.say(self._args)
        tts_engine.runAndWait()


if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
else:
    print("Modul  | {0} | ---> imported".format(__name__))
