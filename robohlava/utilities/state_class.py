import robohlava.robot_class as robot
from robohlava.image_class import ImageProcessing
from robohlava.text_processing import TextProcessor
import robohlava.config as config
import os
import platform

if platform.system() == "Windows":
    import winsound


class StateAutomat:
    """State automat of ROBOHLAVA.

    States:

        0: Sleep_mode:
        1: Waiting: Waiting state
            counter ->
        2: Search person: turn left, turn right
        3: Greeting:
        4: Intro + Analysis of person
        5: Games
        6: Games repeat
        7: Cancel game state

    """
    global state_flags, flags_utilities, flags_image

    state_flags = {
        "sleep": False,
        "wait": False,
        "greeting": False,
        "intro": False,
        "games": False
    }
    flags_utilities = {
        "motors": False,
        "voice": False,
        "touch_display": False,
        "game_book": False,
        "game_yolo": False,
        "person": False,
        "change_person": False,
        "another_person": False
    }
    flags_image = dict(
        tracking=False,
        book=False,
        yolo=False,
        change_person=False,
        display_on=False
    )

    def __init__(self, WIDTH, HEIGHT):

        self.width = WIDTH
        self.height = HEIGHT

        self.robot = robot.Robohlava(WIDTH, HEIGHT) # arduino + voice
        self.ImageProcessing = ImageProcessing(WIDTH, HEIGHT) # images + image proccess
        self.TextProcessor = TextProcessor(os.getcwd())

        self.event = 0
        self.TIMER = 0

        self.current_state = "init"
        self.persons_memory = 0
        self.object_memory = []

        self.game_attempt = 0

        self.text = ""

        self.info = {
            "text_voice": self.text,
            "actual_state": self.current_state
        }

        self.lock = False

        self.states = {
            "init": self.init_mode,
            "sleep": self.waiting_mode,
            "wait": self.waiting_mode,
            "greeting": self.greeting_mode,
            "intro": self.intro_mode,
            "game": self.game_mode,
            "book": self.book_mode,
            "yolo": self.yolo_mode,
            "cancel": self.cancel_mode
        }

        self.TIMER = 0

        self.image = None

        self.snoring_path = os.getcwd() + r"\sound\snoring1"

    def sleep_mode(self, event):
        if event == "on" and not self.lock:
            print("[INFO] going to sleep ...")
            if platform.system() == "Windows":
                winsound.PlaySound(self.snoring_path, winsound.SND_ASYNC | winsound.SND_ALIAS)
            self.lock = True
        elif event == "off" and self.lock:
            print("[INFO] wake up ....")
            if platform.system() == "Windows":
                winsound.PlaySound(None, winsound.SND_ASYNC)

    def init_mode(self):
        for key, value in flags_image.items():
            flags_image[key] = False
        for key, value in flags_utilities.items():
            if key == "motors":
                flags_utilities[key] = True
            else:
                flags_utilities[key] = False
        if self.TIMER > config.init_time:
            self.current_state = "wait"
            print("[State] init -> wait")
            self.TIMER = 0

    def waiting_mode(self):
        flags_image.update(tracking=True)
        flags_image["book"] = False
        flags_image["display_on"] = True
        flags_utilities.update(motors=True)
        # flags_image.update(yolo=True)

        self.TextProcessor.script_stage = 0

        if self.TIMER == 1:
            self.robot.turn(110, 160)

        if self.TIMER == config.search_time_right and not flags_utilities["person"]:
            self.searching_mode("right")
            print("[State] wait -> search")

        elif self.TIMER == config.search_time_left and not flags_utilities["person"]:
            self.searching_mode("left")
        elif self.TIMER == config.search_time_back and not flags_utilities["person"]:
            self.searching_mode("back")
            print("[State] search -> wait")

        elif self.TIMER > config.sleep_time_start and not flags_utilities["person"]:
            self.current_state = "sleep"
            self.sleep_mode("on")
            if self.TIMER > config.sleep_time_end:
                self.sleep_mode("off")
                self.current_state = "wait"
                self.lock = False
                self.TIMER = 0
        elif flags_utilities["person"]:
            self.sleep_mode("off")
            self.lock = False
            self.TIMER = 0
            self.current_state = "greeting"
            print("[State] wait -> greeting")

    def searching_mode(self, side="right"):
        if side == "right":
            self.robot.turn(70, 160)
        elif side == "left":
            self.robot.turn(150, 160)
        else:
            self.robot.turn(110, 160)

    def greeting_mode(self):
        flags_image["tracking"] = True
        flags_utilities["motors"] = True
        flags_image["book"] = False
        flags_image["change_person"] = False
        if not flags_utilities["person"]:
            self.current_state = "wait"
            print("[State] greeting -> wait")
            self.TIMER = 0
            return

        if self.TextProcessor.script_stage >= 3:
            self.TextProcessor.script_stage = 0
            self.current_state = "intro"
            print("[State] greeting -> intro")
            self.TIMER = 0

    def intro_mode(self):
        flags_image["book"] = False
        flags_utilities["touch_display"] = False

        if self.TIMER % 50 == 0:
            flags_image["tracking"] = False
            flags_image["yolo"] = True
        else:
            flags_image["tracking"] = True
            flags_image["yolo"] = False

        if not flags_utilities["person"]:
            self.current_state = "wait"
            print("[State] intro -> wait")
            self.TIMER = 0
            return

        if self.TextProcessor.script_stage >= 3:
            self.TextProcessor.script_stage = 0
            self.current_state = "game"
            print("[State] intro -> game")
            self.TIMER = 0
            return

    def game_mode(self):
        flags_image["tracking"] = True
        flags_image["yolo"] = False
        flags_image["book"] = False
        flags_utilities["touch_display"] = True

        if not flags_utilities["person"] and self.TIMER > config.game_second:
            self.current_state = "wait"
            print("[State] game -> wait")
            self.TIMER = 0
            return

        if self.TIMER > config.game_waiting or self.game_attempt > 3:
            flags_image["change_person"] = True
            if self.game_attempt > 3:
                text = "Strašně jsi mě unavíl, chtěl bych se pobavít s někym \
                        jínym..."
                self.game_attempt = 0
            else:
                text = "Jestli nechceš, zkusím zeptat někoho jíneho!"
            if config.flag_voice:
                self.robot.voice(args=text)
            else:
                print("[INFO] Text to voice: {}".format(text))
            self.current_state = "greeting"
            print("[State] game -> change_person -> greeting")
            self.TIMER = 0
            return

        if flags_utilities["game_book"]:
            self.TextProcessor.script_stage = 0
            self.current_state = "book"
            print("[State] game -> book")
            self.robot.turn(110, 160)
            self.TIMER = 0
            return

        elif flags_utilities["game_yolo"]:
            self.TextProcessor.script_stage = 0
            self.current_state = "yolo"
            print("[State] game -> yolo")
            # self.robot.turn(110, 160)
            self.TIMER = 0
            return

    def book_mode(self):
        flags_image["tracking"] = False
        flags_image["yolo"] = False
        flags_image["book"] = False
        if self.TIMER > config.book_waiting:
            print("[State] book -> game")
            self.current_state = "game"
            self.TIMER = 0
        if self.TIMER > config.book_start:
            flags_image["book"] = True
        if self.TIMER > config.book_stop:
            print("[State] book -> game")
            self.current_state = "game"
            self.TIMER = 0
        if self.TextProcessor.script_stage >= 3:
            print("[State] book -> game")
            self.TextProcessor.script_stage = 0
            self.current_state = "game"
            self.TIMER = 0

    def yolo_mode(self):
        flags_image["tracking"] = True
        flags_image["yolo"] = False
        flags_image["book"] = False

        if self.TIMER > config.yolo_waiting:
            self.current_state = "game"
            print("[State] yolo -> game")
            self.TIMER = 0

        if self.TIMER % 5 == 0 and self.TIMER > config.yolo_start:
            flags_image["tracking"] = False
            flags_image["yolo"] = True
        else:
            flags_image["tracking"] = True
            flags_image["yolo"] = False

        if not flags_utilities["person"]:
            self.current_state = "wait"
            print("[State] intro -> wait")
            self.TIMER = 0
            return

        if self.TextProcessor.script_stage >= 5:
            self.TextProcessor.script_stage = 0
            self.current_state = "game"
            print("[State] yolo -> game")
            self.TIMER = 0
            return

    def how_it_works_mode(self):
        pass

    def cancel_mode(self):
        pass

    def persons_process(self, persons):
        centroid = None
        if persons:
            flags_utilities["person"] = True
            self.persons_memory = 0
        else:
            self.persons_memory += 1
            if self.persons_memory > 100:
                flags_utilities["person"] = False
        if flags_image["tracking"] and flags_utilities["motors"]:
            if persons:
                for person in persons:
                    if person.tracking_person:
                        centroid = person.centroid

                self.robot.calculate_turn_coordinates(centroid)

    def objects_process(self, objects):
        res = []
        for obj in objects:
            for s in obj:
                res.append(s)
        self.object_memory.append(res)

        les = []
        for w in self.object_memory:
            if (w not in les) and w !="person":
                les.append(w)

        self.object_memory = les

    def translated_objects(self):
        final_list = []
        for obj in self.object_memory:
            for w in obj:
                if w not in final_list:
                    final_list.append(w)

        final_str = ""
        for i in final_list:
            if i == "person":
                pass
            else:
                final_str = final_str + i + ", "
        return translate(final_str)


    def terminate(self):
        self.robot.terminate()
        self.ImageProcessing.terminate()


    def run(self, button_flags):
        if button_flags[0]:
            flags_utilities["game_book"] = True
        elif button_flags[1]:
            flags_utilities["game_yolo"] = True
        else:
            flags_utilities["game_book"] = False
            flags_utilities["game_yolo"] = False

        self.info["text_voice"] = self.text
        self.info["actual_state"] = self.current_state

        img_rgb, img_depth, persons, objects = self.ImageProcessing.update(flags_image, self.info)
        self.state_update()
        self.persons_process(persons)

        if self.current_state == "intro" or self.current_state == "yolo":
            self.objects_process(objects)
        else:
            self.object_memory = []

        text = self.TextProcessor.update(self.current_state, persons, self.object_memory, 1)

        if self.current_state == "yolo" and self.TextProcessor.script_stage >= 3:
            text = str(self.TextProcessor.data["object_detection"]["answer"][0]).format(self.translated_objects())
            self.game_attempt += 1
            self.TextProcessor.TIMER = 0
            self.TextProcessor.script_stage = 0
            self.current_state = "game"

        if self.current_state == "book":
            book_text = self.ImageProcessing.book_text
            if not book_text is None:
                text = "Ano už to vidím ... " + book_text
                self.TIMER = -100
                self.TextProcessor.TIMER = 0
                self.TextProcessor.script_stage = 0
                self.current_state = "game"
                self.game_attempt += 1



        if text:
            self.text = text
            if config.flag_voice:
                self.robot.say(text)
            else:
                print("[INFO] Text to voice: {}".format(text))

        return img_rgb, img_depth, self.current_state,  str(text)

    def state_update(self):
        self.states[self.current_state]()
        self.TIMER += 1


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


if __name__ == "__main__":
    import time
    print("Modul  | {0} | ---> executed".format(__name__))
    state = StateAutomat(640, 480)
    state.sleep_mode()
    time.sleep(50)
else:
    print("Modul  | {0} | ---> imported".format(__name__))
