from robohlava.state_machine_base import *
from robohlava.text_processing import Textprocessor
import robohlava.config as conf
import time


def debug(text, var):
    print(f"[DEBUG] {text}, {str(var)}: {var}")


class StateMachine:
    def __init__(self, robohlava_core):
        self.robohlava_core = robohlava_core
        self.text_processor = Textprocessor()
        self.states = []    # list of states
        self.init_state = Init    # hold init state
        self.current_state = self.init_state(self.text_processor)    # Hold current state

    def update_decorator(func):
        def inner(self, *args, **kwargs):
            start_timer = time.time()
            func_return = func(self, *args, **kwargs)
            end_timer = time.time()
            print("Updated timer = {}".format(end_timer-start_timer))
            return func_return
        return inner

    def update(self, triggers):
        """Checks and applies transitions, returning a list of posible
        actions.
        """
        triggered_transition = None

        for transition in self.current_state.get_transitions():
            if transition.is_triggered(triggers):
                triggered_transition = transition
                break

        if triggered_transition:
            # Get target_state and initialize () it
            target_state = triggered_transition.get_target_state()
            target_state = target_state(self.text_processor)
            actions = {}

            actions.update(self.current_state.get_exit_action())
            actions.update(triggered_transition.get_action())
            actions.update(target_state.get_entry_action())

            self.current_state = target_state

            return actions

        else:
            return self.current_state.get_action()


class Init(State):
    def __init__(self, *args):
        super().__init__(*args)
        self.transition1 = Transition(target_state=Wait,
                                    conditions=['local_timer',
                                        conf.timer_init2wait],
                                    state={'timer': self.timer})

        self.transitions.append(self.transition1)

    def get_action(self):
        """Init state actions:

        Motors on
        Camera off
        Text
        """
        actions = {}
        self.timer_next()

        return actions

    def get_exit_action(self):
        self.timer_reset()
        self.stage_reset()
        actions = {}
        actions['voice'] = [conf.init_phrase]
        return actions


class Wait(State):
    def __init__(self, *args):
        super().__init__(*args)
        self.transition1 = Transition(target_state=Search,
                                    conditions=['local_timer',
                                        conf.timer_wait2search],
                                    state={'timer': self.timer})
        self.transition2 = Transition(target_state=Greeting,
                                    conditions=['person'],
                                    state=None)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)

    def get_entry_action(self):
        self.timer_reset()
        self.stage_reset()
        actions = {}
        actions['arduino_turn'] = conf.arduino_base.copy()
        return actions

    def get_action(self):
        actions = {}

        actions["voice"] = self.voice()

        actions["track"] = True
        actions["img_face"] = True

        self.timer_next()
        return actions


class Search(State):
    def __init__(self, *args):
        super().__init__(*args)

        self.transition1 = Transition(target_state=Sleep,
                                    conditions=['local_timer',
                                        conf.timer_search2sleep],
                                    state={'timer': self.timer})
        self.transition2 = Transition(target_state=Greeting,
                                    conditions=['person'],
                                    state=None)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)


    def get_entry_action(self):
        print(self.text)
        actions = {'voice': self.voice()}
        print("entry actions search", actions)
        return actions


    def get_action(self):
        actions = {}

        actions["track"] = True
        actions["img_face"] = True
        if self.timer() == int(conf.timer_search2sleep*1/4):
            print("[INFO] Turn right")
            actions['arduino_turn'] = conf.arduino_right.copy()
        if self.timer() == int(conf.timer_search2sleep*2/4):
            print("[INFO] Turn left")
            actions['arduino_turn'] = conf.arduino_left.copy()
        if self.timer() == int(conf.timer_search2sleep*3/4):
            print("[INFO] Turn base")
            actions['arduino_turn'] = conf.arduino_base.copy()

        self.timer_next()
        return actions


class Sleep(State):
    def __init__(self, *args):
        super().__init__(*args)

        self.transition1 = Transition(target_state=Wait,
                                    conditions=['local_timer', conf.timer_sleep2wait],
                                    state={'timer':self.timer})
        self.transition2 = Transition(target_state=Greeting,
                                    conditions=['person'],
                                    state=None)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)

    def get_entry_action(self):
        actions = {'voice_sleep': True}
        return actions

    def get_action(self):
        actions = {}
        actions['track'] = True
        actions['img_face'] = True

        self.timer_next()
        return actions

    def get_exit_action(self):
        actions = {'voice_sleep': True}
        return actions


class Greeting(State):
    def __init__(self, *args):
        super().__init__(*args)
        self.transition1 = Transition(target_state=Games,
                                    conditions=['and',
                                        [['local_timer', conf.timer_greeting2games],
                                            ['and', [['stage', conf.stage_greeting2games],
                                                'person']]]],
                                    state={'timer'  : self.timer,
                                           'stage'  : self.stage})

        self.transition2 = Transition(target_state=Wait,
                                        conditions=['neg', 'person'],
                                        state=None)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)

    def get_action(self):
        actions = {}
        actions['track'] = True
        actions['img_face'] = True
        if self.stage() == 0:
            actions['img_age'] = True
            actions['img_gender'] = True
        if self.stage() == 1:
            actions['img_age'] = True
            actions['img_gender'] = True
        if self.stage() == 2 or self.stage() == 3:
            if self.timer() % conf.greeting_yolo_ratio == 0:
                actions['img_yolo'] = True
            else:
                pass

        actions['voice'] = self.voice()

        self.timer_next()
        return actions

    def get_entry_action(self):
        actions = {'voice': random.sample(self.text['general'], 1)}
        return actions


    @State.voice_decorator
    def voice(self):
        if self.stage() == 0:
            text = self.text
            self.stage_add()
        elif self.stage() == 1 or self.stage() == 2 or self.stage == 3:
            text = self.text
            self.stage_add()
        elif self.stage() < conf.stage_greeting2games:
            self.stage_add()
            text = ['']
        else:
            text = ['']

        return text



class Games(State):
    INSTANCES = 0
    def __init__(self, *args):
        super().__init__(*args)
        self.transition1 = Transition(target_state=Book,
                                    conditions=['and', [['local_timer',
                                        conf.game_start_delay], 'book']],
                                    state={'timer': self.timer})
        self.transition2 = Transition(target_state=Professor,
                                    conditions=['and', [['local_timer',
                                        conf.game_start_delay], 'professor']],
                                    state={'timer': self.timer})
        self.transition3 = Transition(target_state=Yolo,
                                    conditions=['and', [['local_timer',
                                        conf.game_start_delay], 'yolo']],
                                    state={'timer': self.timer})
        self.transition4 = Transition(target_state=Noname,
                                    conditions=['and', [['local_timer',
                                        conf.game_start_delay], 'noname']],
                                    state={'timer': self.timer})
        self.transition5 = Transition(target_state=Wait,
                                    conditions=['neg', 'person'],
                                    state=None)

        self.transition6 = Transition(target_state=Wait,
                                      conditions=['stage', conf.games_maximum_stage_choice_btn],
                                      state={'stage': self.stage},
                                      actions={'voice': conf.games_change_person_text,
                                               'change_person': True})


        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)
        self.transitions.append(self.transition3)
        self.transitions.append(self.transition4)
        self.transitions.append(self.transition5)
        self.transitions.append(self.transition6)
        self.INSTANCES += 1

    def get_entry_action(self):
        self.timer_reset()
        self.stage_reset()
        actions = {}
        return actions

    def get_action(self):
        actions = {}
        actions['track'] = True
        actions['img_face'] = True
        actions['voice'] = self.voice()
        self.timer_next()
        return actions

    @State.voice_decorator
    def voice(self):
        if self.stage() == 0:
            text = self.text['start']
            self.stage_add()
        elif self.stage() == 1:
            text = random.sample(self.text['general'], 1)
            self.stage_add()
        elif self.stage() == 2:
            text = random.sample(self.text['choice'], 1)
            self.stage_add()
        else:
            text = ['']
            self.stage_add()

        return text



class Game(State):
    def __init__(self, *args):
        super().__init__(*args)
        self.transition = Transition(target_state=Games,
                                    conditions=['cancel'],
                                    state=None,
                                    actions={'voice':
                                        conf.button_cancel_text})
        self.transitions.append(self.transition)

class Book(Game):
    def __init__(self, *args):
        super().__init__(*args)
        self.transition1 = Transition(target_state=Games,
                                    conditions=['local_timer',
                                        conf.timer_book2games],
                                    state={'timer': self.timer},
                                    actions={'voice': self.text['fail']})

        self.transition2 = Transition(target_state=Games,
                                    conditions=['end'],
                                    state=None)

        self.transitions.append(self.transition1)


    def get_entry_action(self):
        self.timer_reset()
        self.stage_reset()
        text = random.sample(self.text['other'], 1)
        return {'voice': text}

    def get_action(self):
        actions = {}
        if self.timer() > conf.timer_book_start:
            actions['img_book'] = True
        self.timer_next()
        return actions



class Yolo(Game):
    def __init__(self, *args):
        super().__init__(*args)
        self.transition1 = Transition(target_state=Games,
                                    conditions=['local_timer',
                                        conf.timer_yolo2games],
                                    state={'timer': self.timer},
                                    actions={'yolo_end': True})

        self.transitions.append(self.transition1)

    def get_entry_action(self):
        self.timer_reset()
        self.stage_reset()
        text = random.sample(self.text['start'], 1)
        actions = {'voice': text}
        return actions

    def get_action(self):
        actions = {}
        if self.timer() > conf.timer_yolo_start:
            if self.timer() % conf.yolo_ratio == 0:
                actions['img_yolo'] = True

        self.timer_next()
        return actions



class Professor(Game):
    def __init__(self, *args):
        super().__init__(*args)


class Noname(Game):
    def __init__(self, *args):
        super().__init__(*args)


