import sys
import time

def animated_loading():
    """
    Animation for loading.
    :return:
    """
    chars = "/—\|"
    for char in chars:
        sys.stdout.write('\r' + char)
        time.sleep(.1)
        sys.stdout.flush()
    sys.stdout.write('\r')



def translate(text):
    eng_text = ["person", "tie", "backpack", "bottle", "cup", "banana", "apple", "sandwich", "orange",
                "chair", "diningtable", "tvmonitor", "laptop", "mouse", "remote", "keyboard",
                "cell phone", "book", "clock" "pottedplant"]
    cz_text = ["človeka", "kravata", "batoh", "lahev", "hrnek", "banan", "jabko", "chlebiček", "pomeranč",
               "židle", "stul", "obrazovka", "počitač", "myš", "dalkové ovladaní", "klavisnice",
               "telefon", "kniha", "hodinky", "květ"]
    dict_eng_cz = dict(zip(eng_text, cz_text))
    text_to_voice_cz = replace_all(text, dict_eng_cz)
    print(text_to_voice_cz)
    return text_to_voice_cz

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


class Lock:
    """Locker function.
    state = True -> unlock
    state = False -> lock
    """
    def __init__(self):
        self.state = True

    def __repr__(self):
        return "Locker"

    def __call__(self):
        return self.state

    def unlocked(self):
        return self.state

    def lock(self):
        self.state = False

    def unlock(self):
        self.state = True

    def toggle(self):
        self.state = not self.state


class Counter:
    def __init__(self):
        self.count = 0

    def __repr__(self):
        return f"Counter: {self.count}"

    def __call__(self):
        return self.count

    def __iadd__(self, other:int):
        self.count = self.count + other
        return self

    def reset(self):
        self.count = 0
