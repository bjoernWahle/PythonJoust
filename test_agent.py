import numpy as np
import keras
from keras.layers import Dense
import logging

from qlearning_utils import Discretizer


class NaiveAgent():
    """
            This is our naive agent. It picks actions at random!
    """

    def __init__(self, player, actions, state_space, train_start=0, exploration_prob_init=0.1, exporation_prop_decay=0.9, y=0.95, log_level=logging.WARNING):

        self.player = player
        self.id = player.id
        self.state_space = state_space
        self.action_keys = actions.keys()
        self.actions = actions.values()
        self.history = []
        self.last_state = None
        self.last_action = None

        x_steps = 10
        y_steps = 10
        x_min = 0
        x_max = 900
        y_min = 0
        y_max = 650
        x_speed_steps = 10
        y_speed_steps = 10
        x_speed_min = -10
        x_speed_max = 10
        y_speed_min = -10
        y_speed_max = -10

        #self._d = Discretizer(np.array([]))

        self.train_start = train_start
        self.y = y
        self.exploration_prob = exploration_prob_init
        self.exploration_prob_decay = exporation_prop_decay

        self.logger = logging.Logger("P%i" % self.id)
        self.logger.setLevel(log_level)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)

        self.nn = self._buildNN()

    def pick_action(self, state, rewards, time):

        if time > 0 and  time % 10000 == 0:
            self.exploration_prob = self.exploration_prob*self.exploration_prob_decay
            self.logger.info("Exploration prob decreased to %f" % self.exploration_prob)

        if self.player.alive == 2 and not self.player.spawning:
            if np.random.uniform() < self.exploration_prob:
                action_idx = np.random.randint(0, len(self.actions))
            else:
                action_idx = self._predict_action(state)
                self.logger.debug("Predicted action: %s" % self.action_keys[action_idx])
            self.last_state = state
            self.last_action = action_idx
            self.alive_last_round = True
            return self.actions[action_idx]
        else:
            self.alive_last_round = False
            self.last_state = None
            self.last_action = None
            return self.actions[self.action_keys.index("p%i_noop" % self.id)]


    def _buildNN(self):
        nn = keras.Sequential()
        nn.add(Dense(units=len(self.actions), input_dim=self.state_space[1]))
        nn.compile(loss='mse',
                   optimizer='adam')

        return nn

    def _predict_action(self, state):
        return np.argmax(self.nn.predict(state))

    def train(self, rewards, new_state):
        if self.last_state is not None and self.alive_last_round:
            self.history.append([self.last_state, self.last_action, rewards])
            # get own reward
            r = rewards[self.id - 1]

            target = r + self.y * np.max(self.nn.predict(new_state)) - self.nn.predict(self.last_state)[0][self.last_action]
            target_vec = self.nn.predict(self.last_state)[0]
            target_vec[self.last_action] = target
            self.nn.fit(self.last_state, target_vec.reshape(-1, len(self.actions)), epochs=1, verbose=False)
