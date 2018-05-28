import math

import numpy as np
import logging


class RuleBasedAgent():
    def __init__(self, player, actions, cooperating=True, log_level=logging.WARNING):
        self.player = player
        self.id = player.id
        self.action_keys = actions.keys()
        self.actions = actions.values()
        self.rewards = []
        self.last_state = None
        self.last_action = None

        self.cooperating = cooperating

        self.logger = self.init_logger(log_level)

    def init_logger(self, log_level):
        logger = logging.Logger("P%i" % self.id)
        logger.setLevel(log_level)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)
        return logger

    def pick_action(self, state, rewards, time):

        action_idx = None
        other_player = self.get_other_player_state(state)

        if self.cooperating:
            if self.distance_to(other_player['x'], other_player['y']) < 150.0:
                reverted_x_speed, reverted_y_speed = self.get_reverted_vector(other_player['x'], other_player['y'])
                if np.abs(reverted_x_speed) > np.abs(reverted_y_speed) or self.player.y < 50:
                    if reverted_x_speed>0:
                        action_idx = self.get_action_index("right")
                    else:
                        action_idx = self.get_action_index("left")
                else:
                    if reverted_y_speed>0:
                        action_idx = self.get_action_index("noop")
                        self.logger.info("Going down")
                    else:
                        action_idx = self.get_action_index("up")

        if self.player.y > 500:
            action_idx = self.get_action_index("up")

        if action_idx is None:
            action_idx = np.random.randint(0, len(self.actions))

        self.last_state = state
        self.last_action = action_idx
        return self.actions[action_idx]

    def get_action_index(self, action_key):
        return self.action_keys.index("p%i_%s" % (self.id, action_key))

    def store_reward(self, rewards):
        self.rewards.append(rewards[self.id - 1])

    def get_other_player_state(self, state):
        if self.id == 1:
            p_state = state[4:]
        else:
            p_state = state[:4]

        return {'x': p_state[0], 'y': p_state[2], 'x_speed': p_state[1], 'y_speed': p_state[3]}

    def distance_to(self, o_x, o_y):
        return math.sqrt(((self.player.x - o_x) ** 2) + ((self.player.y - o_y) ** 2))

    def get_reverted_vector(self, x, y):
        return (x-self.player.x) * -1.0, (y-self.player.y) * -1.0
