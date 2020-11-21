from robohlava.state_machine import StateMachine
from robohlava.image_class import ImageProcessing
from robohlava.robot_class import Robohlava
from robohlava.tools import Lock, Counter, translate
import robohlava.config as conf
import os
import platform

if platform.system() == "Windows":
    import winsound

class RobohlavaCore:
    """RobohlavaCore Functions:

        Robohlava provide this functions:

            1. Take frame
            2. Frame process
            3. Save data from frame
            4. Arduino
            5. Voice
            6. Change person
            7. Another person TODO

        Possible triggers for StateMachine:

            0. end (stage > N) #internal?
            1. person in frame
            4. objects in frame
            3. timer information
            4. book
            5. professor
            6. yolo
            7. noname
            8. cancel

        PyQt communication:

            1. Input qt_input - buttons information:
                -1 -> cancel state, return to game
                 0 -> nothing
                 1 -> book
                 2 -> explain
                 3 -> yolo
                 4 -> don't know
            2. Output:
                img_rgb
                img_depth
                persons[info, image]
                objects[info, image]
                main_window_on
                touch_window_on

        Actions:

    """

    triggers_list = {'end'      : False,
                    'person'    : False,
                    'object'    : False,
                    'timer'     : False,
                    'book'      : False,
                    'professor' : False,
                    'yolo'      : False,
                    'noname'    : False,
                    'cancel'    : False
                    }

    actions_list = {'track'             : False,
                    'img_face'          : False,
                    'img_gender'        : False,
                    'img_age'           : False,
                    'img_yolo'          : False,
                    'img_book'          : False,
                    'change_person'     : False,
                    'disp_show_main'    : False,
                    'disp_show_touch'   : False,
                    'disp_btns_act'     : False,
                    'arduino_turn'      : [],
                    'voice'             : [''],
                    'voice_sleep'       : False,
                    'Gtime_reset'       : False,
                    'yolo_end'          : False}


    def __init__(self):
        self.state_machine = StateMachine(self)
        self.ImageProcessing = ImageProcessing()
        self.robot = Robohlava()

        self.Gtimer = 0
        self.locker_voice = Lock()
        self.count_person = Counter()
        self.locker_person = Lock()

        self.triggers = self.triggers_list.copy()
        self.actions = self.actions_list.copy()
        self.voice_text = ""
        self.snoring_path = os.getcwd() + r"\sound\snoring1"

        self.object_memory = []

    def run(self, qt_input):
        """Run method
        """
        self.actions_reset()

        actions = self.state_machine.update(self.triggers)

        self.actions.update(actions)
        img_flags = self.actions_process()
        rgb, depth, mini, persons, objects, book_text = self.ImageProcessing.update(img_flags)


        self.persons, self.objects = persons, objects

        triggers = {'person'    : persons,
                    'objects'   : objects,
                    'book_text' : book_text,
                    'qt_input'  : qt_input}

        self.triggers_process(triggers)

        if self.Gtimer >= 1000:
            self.Gtimer = 0

        self.Gtimer += 1
        data2qt = {'rgb'        : rgb,
                   'depth'      : depth,
                   'mini'       : mini,
                   'state'      : self.state_machine.current_state.name,
                   'text'       : self.voice_text,
                   'num_persons': len(persons)}

        return data2qt

    def persons_process(self, persons):
        centroid = None
        if self.actions['track']:
            if persons:
                for person in persons:
                    if person.tracking_person:
                        centroid = person.centroid
                self.robot.calculate_turn_coordinates(centroid)

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


    def triggers_process(self, triggers):
        self.triggers['timer'] = self.Gtimer
        self.triggers['end'] = False
        for key, value in triggers.items():
            if key == 'qt_input':
                self.triggers['book'] = value[0]
                self.triggers['professor'] = value[1]
                self.triggers['yolo'] = value[2]
                self.triggers['noname'] = value[3]
                self.triggers['cancel'] = value[4]

            if key == 'person':
                if self.actions['track']:
                    if any(value):
                        if self.locker_person.unlocked():
                            if self.count_person() > conf.num_person2track:
                                self.triggers[key] = True
                                self.locker_person.lock()
                                self.count_person.reset()
                            else:
                                self.count_person += 1
                        self.persons_process(value)
                    else:
                        if not self.locker_person.unlocked():
                            if self.count_person() > conf.num_person2untrack:
                                self.triggers[key] = False
                                self.locker_person.unlock()
                                self.count_person.reset()
                            else:
                                self.count_person += 1
            if key == 'book_text':
                if self.state_machine.current_state.name == 'Book':
                    if value is not None:
                        text = self.state_machine.current_state.text['success'][0].format(value)
                        self.robot.say(text)
                        self.voice_text = text
                        self.triggers['end'] = True
                    else:
                        self.triggers['end'] = False

            if key == 'objects':
                if self.state_machine.current_state.name in ['Yolo', 'Greeting']:
                    self.objects_process(value)
                else:
                    if self.Gtimer % 20 == 0:
                        self.object_memory = []


    def actions_process(self):
        image_processing_flags = {}
        for key, value in self.actions.items():
            if key == 'track':
               image_processing_flags[key] = value
            if key == 'img_face':
               image_processing_flags[key] = value
            if key == 'img_gender':
               image_processing_flags[key] = value
            if key == 'img_age':
               image_processing_flags[key] = value
            if key == 'img_yolo':
                image_processing_flags[key] = value
            if key == 'change_person':
                image_processing_flags[key] = value
            if key == 'img_book':
                image_processing_flags[key] = value
            if key == 'disp_show_main':
                image_processing_flags[key] = value
            if key == 'disp_show_touch':
                pass
            if key == 'disp_btns_act':
                pass
            if key == 'arduino_turn':
                if any(value):
                    self.robot.turn(value[0], value[1])

            if key == 'yolo_end':
                if value:
                    text = conf.yolo_end_text + self.translated_objects()
                    self.robot.say(text)
                    self.voice_text = text
                    break

            if key == 'voice':
                if self.state_machine.current_state.name == 'Greeting':
                    stage = self.state_machine.current_state.stage()
                    if any(value):
                        text = ''
                        if stage == 1:
                            if len(self.persons) > 1:
                                text = value["more_people"]
                            else:
                                text = value["pay"]

                        elif stage == 2:
                            for person in self.persons:
                                if person.tracking_person:
                                    if (person.gender == "Female" and
                                            (person.age == "(4,6)" or
                                                person.age == "(8,12)")):
                                        text = value["kid"]
                                    elif person.gender == "Male" and person.age == "(48,53)":
                                        text = value["vec"]
                                    else:
                                        text = value["name"]
                                else:
                                    text = ''

                        elif stage == 3:
                            if any(self.object_memory):
                                for obj in self.object_memory:
                                    if "telefon" in obj:
                                        text = value["telefon"]
                                    elif "batoh" in obj:
                                        text = value["batoh"]
                                    elif "kravata" in obj:
                                        text = value["kravata"]
                                    else:
                                        text = value["dialog"]
                            else:
                                text = value["dialog"]
                        else:
                            text = ''
                        self.voice_text = text
                        self.robot.say(text)

                elif any(value):
                    if conf.flag_voice:
                        self.robot.say(value[0])
                    self.voice_text = value[0]

            if key == 'voice_sleep':
                if value:
                    if self.locker_voice.unlocked():
                        if platform.system() == "Windows":
                            winsound.PlaySound(self.snoring_path,
                                    winsound.SND_ASYNC | winsound.SND_ALIAS)
                        self.locker_voice.lock()
                    else:
                        if platform.system() == "Windows":
                            winsound.PlaySound(None, winsound.SND_ASYNC)
                        self.locker_voice.unlock()
                else:
                    pass

            if key == 'Gtimer_reset':
                if value:
                    self.Gtimer = 0

        return image_processing_flags

    def actions_reset(self):
        self.actions.update(self.actions_list)

    def terminate(self):
        self.robot.terminate()
        self.ImageProcessing.terminate()

if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
else:
    print("Modul  | {0} | ---> imported".format(__name__))
