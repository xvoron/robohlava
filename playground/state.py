import time
import random
from state_machine import *
voice_padding = 10


class Init(State):
    def __init__(self):
        super().__init__()
        self.transition1 = Transition(target_state=Wait,
                                    conditions=['timer', 5],
                                    state=None)

        self.transitions.append(self.transition1)

    def get_action(self):
        """Init state actions:

        Motors on
        Camera off
        Text
        """
        return list()


class Wait(State):
    def __init__(self):
        super().__init__()
        self.transition1 = Transition(target_state=Search,
                                    conditions=['timer', 10],
                                    state=None)
        self.transition2 = Transition(target_state=Greeting,
                                    conditions=['person'],
                                    state=None)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)

        self.text = ["luuuzr", "ahoj", "total loser"]

    def get_action(self):

        global voice_padding
        if self.timer() > voice_padding:
            self.actions["voice"] = random.sample(self.text, 1)
            self.timer_reset()

        self.actions["tracker"] = True
        self.actions["arduino"] = "on"

        self.timer_next()
        return list(self.actions)




class Search(State):
    def __init__(self):
        super().__init__()

        self.transition1 = Transition(target_state=Sleep,
                                    conditions=['timer', 15],
                                    state=None)
        self.transition2 = Transition(target_state=Greeting,
                                    conditions=['person'],
                                    state=None)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)


class Sleep(State):
    def __init__(self):
        super().__init__()

        self.transition1 = Transition(target_state=Wait,
                                    conditions=['timer', 20],
                                    state=None)
        self.transition2 = Transition(target_state=Greeting,
                                    conditions=['person'],
                                    state=None)

        self.transition3 = Transition(target_state=Wait,
                                    conditions=['local_timer', 10],
                                    state=self.timer)

        self.transitions.append(self.transition1)
        self.transitions.append(self.transition2)
        self.transitions.append(self.transition3)

    def get_action(self):
        print("get_action", self.timer())

        self.timer_next()
        return list(self.actions)


class Greeting(State):
    def __init__(self):
        pass


class StateMachine:
    def __init__(self, robohlava_core):
        self.robohlava_core = robohlava_core
        self.states = []    # list of states
        init_state = Init    # hold init state
        self.current_state = init_state()    # Hold current state

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
            target_state = (triggered_transition.get_target_state())()

            actions = self.current_state.get_exit_action()
            actions += triggered_transition.get_action()
            actions += target_state.get_entry_action()

            self.current_state = target_state
            return actions

        else:
            return self.current_state.get_action()


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
            1. Person in frame
            2. Timer information
            3. Button from user
            4. Objects in frame

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

    triggers_list = {'end':False,
                    'person':False,
                    'timer':False,
                    'button':False,
                    'object':False}


    def __init__(self):
        self.state_machine = StateMachine(self)
        #self.ImageProcessing = ImageProcessing(config.WIDTH, config.HEIGHT)
        #self.robot = robot.Robohlava(config.WIDTH, config.HEIGHT)
        #self.TextProcessor = TextProcessor(os.getcwd()) # TODO Legacy

        self.Gtimer = 0

        self.triggers = self.triggers_list

    def run(self, qt_input):
        """Run method

        """
        actions = self.state_machine.update(self.triggers)
        print("Current state:", self.state_machine.current_state)

        self.triggers['timer'] = self.Gtimer

        print("Triggers: ", self.triggers)
        self.Gtimer += 1

        #self.actions_process(actions)
        if self.Gtimer >= 20:
            self.Gtimer = 0

        time.sleep(.5)

        return

    def triggers_process(self, triggers):
        return triggers

    def actions_process(self, actions):
        print("[INFO]", actions)
        if actions is not None:
            for action in actions:
                for flag_name, flag in actions.items():
                    print(flag_name, flag)
                return actions



if __name__ == "__main__":
    robohlava = RobohlavaCore()
    t = 0
    while t<100:
        robohlava.run(None)




