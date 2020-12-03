import os
import json
import random

import robohlava.config as conf
import platform

class Textprocessor:
    """

    return dict()
    """

    def __init__(self, base_dir=""):
        if not base_dir:
            if __name__ == "__main__":
                base_dir = os.getcwd() + r"\.."
            else:
                base_dir = os.getcwd()

        if platform.system() == "Windows":
            json_path = base_dir + r"\json\text.json"
            rur_path = base_dir + r"\txt_file\rur.txt"
        else:
            json_path = base_dir + r"/json/text.json"
            rur_path = base_dir + r"/txt_file/rur.txt"

        print("path", json_path)
        with open(json_path, 'r', encoding='utf-8') as f1:
            self.data = json.load(f1)
            f1.close()
        with open(rur_path, 'r', encoding='utf-8') as f2:
            self.rur_text = f2.read()
            f2.close()

        self.text = []
        self.states_functions = {'Init'     : self.init_process,
                                 'Wait'     : self.wait_process,
                                 'Search'   : self.search_process,
                                 'Sleep'    : self.sleep_process,
                                 'Greeting' : self.greeting_process,
                                 'Games'    : self.games_process,
                                 'Book'     : self.book_process,
                                 'Professor': self.professor_process,
                                 'Yolo'     : self.yolo_process,
                                 'Noname'   : self.noname_process}


    def run(self, current_state):
        """Return dict() with texts"""
        return self.states_functions[current_state]()

    def init_process(self):
        return self.data['init']

    def wait_process(self):
        return self.data['wait']

    def search_process(self):
        return self.data['search']

    def sleep_process(self):
        return self.data['sleep']

    def greeting_process(self):
        return self.data['greeting']

    def games_process(self):
        return self.data['games']

    def book_process(self):
        return (self.data['book'], self.rur_text)

    def professor_process(self):
        return self.data['professor']

    def yolo_process(self):
        return self.data['yolo']

    def noname_process(self):
        return self.data['noname']


if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
else:
    print("Modul  | {0} | ---> imported".format(__name__))
