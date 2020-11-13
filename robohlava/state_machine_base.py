import random
import robohlava.config as conf

class State:
    def __init__(self, *args):
        self.text_processor = args[0]
        self.transitions = []
        self.local_timer = 0
        self.local_stage = 0
        self.voice_timer = 0
        self.text = []
        self.voice_padding_constant = conf.voice_padding_constant
        self.voice_padding = conf.voice_padding_init
        self.name = type(self).__name__
        self.text = self.text_processor.run(self.name)

    def __repr__(self):
        return str(self.name)

    def get_action(self):
        return dict()

    def get_entry_action(self):
        self.timer_reset()
        self.stage_reset()
        return dict()

    def get_exit_action(self):
        self.timer_reset()
        self.stage_reset()
        return dict()

    def get_transitions(self):
        return self.transitions

    def timer(self):
        return self.local_timer

    def timer_next(self):
        self.local_timer += 1

    def timer_reset(self):
        self.local_timer = 0

    def stage(self):
        return self.local_stage

    def stage_add(self):
        self.local_stage += 1

    def stage_reset(self):
        self.local_stage = 0

    def voice_decorator(func):
        def inner(self, *args, **kwargs):
            if self.voice_timer > self.voice_padding:
                text = func(self)
                try:
                    self.voice_padding = int(len(text[0])*self.voice_padding_constant)
                except:
                    self.voice_padding = int(conf.voice_padding_init*self.voice_padding_constant)
                self.voice_timer = 0
                return text
            else:
                self.voice_timer += 1
                return ['']
        return inner

    @voice_decorator
    def voice(self):
        return random.sample(self.text['general'], 1)


class Transition:
    def __init__(self, target_state, conditions, state, actions=None):
        self.target_state = target_state
        self.conditions = ConditionBase(conditions, state)
        if actions is not None:
            self.actions = actions
        else:
            self.actions = {}

    def is_triggered(self, triggers):
        return self.conditions.test(triggers)

    def get_target_state(self):
        return self.target_state

    def get_action(self):
        return self.actions


class ConditionBase:
    def __init__(self, conditions, state):

        if type(conditions) == list:
            if len(conditions) >= 2:

                if conditions[0] == 'and':
                    self.condition = ANDCondition(conditions[1:][0],
                            state)

                if conditions[0] == 'timer':
                    self.condition = TIMERCondition(conditions[1:][0])

                if conditions[0] == 'neg':
                    self.condition = NEGCondition(conditions[1])

                if conditions[0] == 'local_timer':
                    if state['timer'] is not None:
                        self.condition = LOCALTIMERCondition(conditions[1:][0],
                                state['timer'])
                    else:
                        print("[ERROR] State is None")

                if conditions[0] == 'stage':
                    if state['stage'] is not None:
                        self.condition = STAGECondition(conditions[1:][0],
                                state['stage'])
                    else:
                        print("[ERROR] State is None")

            else:
                self.condition = ConditionBase(conditions[0], state)

        else:
            self.condition = Condition(conditions)


    def test(self, triggers):
        return self.condition.test(triggers)



class Condition:
    """Must have resources on robohlvava core
    Condition to transition
    """

    def __init__(self, trigger):
        self.trigger = trigger

    def test(self, triggers):
        """Test the condition.

        Arguments:
            * triggers:dict - actual triggers from robohlava:
                {'end':Bool, 'person':Bool, ... }
        Return:
            * True/False
        """
        return triggers[self.trigger]


class NEGCondition:
    def __init__(self, trigger):
        self.trigger = trigger

    def test(self, triggers):
        return not triggers[self.trigger]


class TIMERCondition:
    def __init__(self, timer_max):
        self.timer_max = timer_max

    def test(self, triggers):
        return triggers['timer'] >= self.timer_max


class LOCALTIMERCondition:
    def __init__(self, timer_max, timer):
        self.timer_max = timer_max
        self.timer = timer

    def test(self, triggers):
        return self.timer() >= self.timer_max


class STAGECondition:
    def __init__(self, stage_max, stage):
        self.stage_max = stage_max
        self.stage = stage

    def test(self, triggers):
        return self.stage() >= self.stage_max


class ANDCondition:
    def __init__(self, conditions, state):
        super().__init__()
        self.condition_A = ConditionBase(conditions[0], state)
        self.condition_B = ConditionBase(conditions[1], state)

    def test(self, triggers):
        return (self.condition_A.test(triggers) and
                self.condition_B.test(triggers))

class ORCondition:
    def __init__(self, conditions, state):
        super().__init__()
        self.condition_A = ConditionBase(conditions[0], state)
        self.condition_B = ConditionBase(conditions[1], state)

    def test(self, triggers):
        return (self.condition_A.test(triggers) or
                self.condition_B.test(triggers))


