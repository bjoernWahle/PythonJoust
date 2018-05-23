import numpy as np


class NaiveAgent():
    """
            This is our naive agent. It picks actions at random!
    """



    def __init__(self, actions, state_space):
        self.state_space = state_space
        self.actions = actions.values()

    def pick_action(self, state):
        return self.actions[np.random.randint(0, len(self.actions))]
