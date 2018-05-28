import math

import numpy as np
import logging


def get_vector_length(x,y):
    return math.sqrt(x**2 + y**2)


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

        # don't kill each other rule
        if self.cooperating:
            if self.distance_to(other_player['x'], other_player['y']) < 150.0:
                action_idx = self.move_away_from(other_player['x'], other_player['y'])

        enemies = self.player.game.get_enemies()
        close_enemies = []
        for enemy in enemies:
            if enemy.alive:
                dx, dy = self.get_distance_vector(enemy.x,enemy.y)
                distance =get_vector_length(dx, dy)
                if distance < 150.0:
                    close_enemies.append((enemy, (dx,dy), distance))

        # kill enemy rule: try to kill closest enemy below
        closest_enemy_below = None
        closest_below_distance = 9999
        for enemy, (dx, dy), distance in close_enemies:
            if dy > 0 and distance < closest_below_distance:
                closest_enemy_below = enemy
                closest_below_distance = distance
        if closest_enemy_below is not None:
            self.logger.info("I gonna kill that enemy!")
            action_idx = self.move_towards(closest_enemy_below.x, closest_enemy_below.y)

        # don't get killed rule: try to move away from closest enemy above
        closest_enemy_above = None
        closest_above_distance = 9999
        for enemy, (dx, dy), distance in close_enemies:
            if dy < 0 and distance < closest_above_distance:
                closest_enemy_above = enemy
                closest_above_distance = distance
        if closest_enemy_above is not None:
            self.logger.info("I gonna fly away from that enemy!")
            action_idx = self.move_away_from(closest_enemy_above.x, closest_enemy_above.y)

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
        dx, dy = self.get_distance_vector(o_x, o_y)
        return get_vector_length(dx, dy)

    def get_reverted_vector(self, x, y):
        dx, dy = self.get_distance_vector(x, y)
        return dx * -1.0, dy * -1.0

    def move_away_from(self, o_x, o_y):
        reverted_x_speed, reverted_y_speed = self.get_reverted_vector(o_x, o_y)
        if np.abs(reverted_x_speed) > np.abs(reverted_y_speed) or self.player.y < 50:
            if reverted_x_speed > 0:
                action_idx = self.get_action_index("right")
            else:
                action_idx = self.get_action_index("left")
        else:
            if reverted_y_speed > 0:
                action_idx = self.get_action_index("noop")
            else:
                action_idx = self.get_action_index("up")
        return action_idx

    def get_distance_vector(self, x, y):
        return x - self.player.x, y- self.player.y

    def move_towards(self, x, y):
        dx, dy = self.get_distance_vector(x, y)
        if np.abs(dx) > np.abs(dy) or self.player.y < 50:
            if dx > 0:
                action_idx = self.get_action_index("right")
            else:
                action_idx = self.get_action_index("left")
        else:
            if dy > 0:
                action_idx = self.get_action_index("noop")
            else:
                action_idx = self.get_action_index("up")
        return action_idx
