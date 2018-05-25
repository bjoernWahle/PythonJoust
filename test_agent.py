import numpy as np
import keras
from keras.layers import Dense
import logging

from qlearning_utils import Discretizer


class NaiveAgent():
    """
            This is our naive agent. It picks actions at random!
    """

    def __init__(self, player, actions, state_space, train_start=0, exploration_prob_init=1, exploration_prob_train=0.2, exporation_prop_decay=0.9, y=0.95, log_level=logging.WARNING):
        self.exploration_prob_train = exploration_prob_train
        self.player = player
        self.id = player.id
        self.state_space = state_space
        self.action_keys = actions.keys()
        self.actions = actions.values()
        self.rewards = []
        self.last_state = None
        self.last_action = None

        self.train_start = train_start
        self.y = y
        self.exploration_prob = exploration_prob_init
        self.exploration_prob_decay = exporation_prop_decay

        self.logger = logging.Logger("P%i" % self.id)
        self.logger.setLevel(log_level)

        self.q_list = []

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
            qAll, action_idx = self._predict_action(state)
            self.logger.debug("Predicted action: %s" % self.action_keys[action_idx])
            if np.random.uniform() < self.exploration_prob:
                action_idx = np.random.randint(0, len(self.actions))

            self.q_list.append([state, qAll, action_idx])

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
        nn.add(Dense(units=len(self.actions),activation="softmax", input_dim=self.state_space[1]))
        nn.compile(loss='mse',
                   optimizer='adam')

        return nn

    def _predict_action(self, state):
        q_all = self.nn.predict(state)[0]
        return q_all, np.argmax(q_all)

    def store_reward(self, rewards):
        self.rewards.append(rewards[self.id - 1])

    def train(self, rewards, new_state):
        if self.last_state is not None and self.alive_last_round:
            # get own reward
            r = rewards[self.id - 1]

            target = r + self.y * np.max(self.nn.predict(new_state)) - self.nn.predict(self.last_state)[0][self.last_action]
            target_vec = self.nn.predict(self.last_state)[0]
            target_vec[self.last_action] = target
            self.nn.fit(self.last_state, target_vec.reshape(-1, len(self.actions)), epochs=1, verbose=False)

    def replay_memories(self, final_reward1):
        X = np.zeros([len(self.q_list), self.state_space[1]])
        Y = np.zeros([len(self.q_list), len(self.actions)])
        for index, (state, qAll, a_i) in enumerate(self.q_list):
            qAll[a_i] = final_reward1
            Y[index, :] = qAll
            X[index] = state

        self.nn.fit(X, Y, epochs=1, verbose=False)
        self.q_list = []
