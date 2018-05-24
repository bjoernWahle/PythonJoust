import numpy as np
import keras
from keras.layers import Dense


class NaiveAgent():
    """
            This is our naive agent. It picks actions at random!
    """
    def __init__(self, id, actions, state_space):
        self.id = id
        self.state_space = state_space
        self.action_keys = actions.keys()
        self.actions = actions.values()
        self.history = []
        self.last_state = None
        self.last_action = None
        self.exploration_prob = 0.5

        self.y = 0.95

        self.nn = self._buildNN()

    def pick_action(self, state, rewards):
        if self.last_state is not None:
            self.train(rewards, state)
            self.history.append([self.last_state, self.last_action, rewards])
        if np.random.uniform() > self.exploration_prob:
            action_idx = np.random.randint(0, len(self.actions))
        else:
            action_idx = self._predict_action(state)
            print("Player %s predicted action: %s" % (str(self.id), self.action_keys[action_idx]))
        self.last_state = state
        self.last_action = action_idx
        return self.actions[action_idx]


    def _buildNN(self):
        nn = keras.Sequential()
        nn.add(Dense(units=64, activation='relu', input_dim=self.state_space[1]))
        nn.add(Dense(units=len(self.actions), activation='softmax'))
        nn.compile(loss='mse',
                      optimizer='adam')
        return nn

    def _predict_action(self, state):
        return np.argmax(self.nn.predict(state))

    def train(self, rewards, new_state):
        # get own reward
        r = rewards[self.id-1]
        target = r + self.y * np.max(self.nn.predict(new_state))
        print(self.last_state)
        target_vec = self.nn.predict(self.last_state)[0]
        target_vec[self.last_action] = target
        self.nn.fit(self.last_state, target_vec.reshape(-1, 4), epochs=1, verbose=False)
