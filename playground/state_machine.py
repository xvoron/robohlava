class State:
    def __init__(self):
        self.transitions = []
        self.actions = {}
        self.local_timer = 0
        self.local_stage = 0

    def get_action(self):
        return list(self.actions)

    def get_entry_action(self):
        return list(self.actions)

    def get_exit_action(self):
        return list(self.actions)

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



class Transition:
    def __init__(self, target_state, conditions, state):
        self.target_state = target_state
        self.conditions = ConditionBase(conditions, state)
        self.actions = {}

    def is_triggered(self, triggers):
        return self.conditions.test(triggers)

    def get_target_state(self):
        return self.target_state

    def get_action(self):
        return list(self.actions)


class ConditionBase:
    def __init__(self, conditions, state):
        print("Conditions: ", conditions)
        self.state = state

        if type(conditions) == list:
            if len(conditions) >= 2:

                if conditions[0] == 'and':
                    self.condition = ANDCondition(conditions[1:][0])

                if conditions[0] == 'timer':
                    print("init_condition_timer", conditions[1:][0])
                    self.condition = TIMERCondition(conditions[1:][0])

                if conditions[0] == 'local_timer':
                    if self.state is not None:
                        self.condition = LOCALTIMERCondition(conditions[1:][0],
                                self.state)
                    else:
                        print("[ERROR] State is None")

                if conditions[0] == 'stage':
                    if self.state is not None:
                        self.condition = STAGECondition(conditions[1:][0],
                                self.state.local_stage)
                    else:
                        print("[ERROR] State is None")

            else:
                self.condition = ConditionBase(conditions[0], state)

        else:
            print("init condition", type(conditions), conditions)
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
        print(f"Local timer condition: {self.timer()}, {self.timer_max}")
        return self.timer() >= self.timer_max


class STAGECondition:
    def __init__(self, stage_max, stage):
        self.stage_max = stage_max
        self.stage = stage

    def test(self, triggers):
        return self.stage >= self.stage_max


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



