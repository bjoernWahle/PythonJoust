import logging
import sys

import pygame

from ple import PLE
from sklearn.preprocessing import MinMaxScaler

from Joust import Joust
from rule_base_agent import RuleBasedAgent
from test_agent import NaiveAgent
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sklearn

def process_state(state):
    return np.array([
        state['player1_x'],
        state['player1_x_speed'],
        state['player1_y'],
        state['player1_y_speed'],
        state['player2_x'],
        state['player2_x_speed'],
        state['player2_y'],
        state['player2_y_speed'],
    ]).reshape(1, -1)[0]


game = Joust(display_screen=True)

p = PLE(game, fps=30, display_screen=False, state_preprocessor=process_state, force_fps=False)
p.init()
player1 = game.player1
player2 = game.player2
agent1 = RuleBasedAgent(player1, game.p1_actions, cooperating=True, log_level=logging.INFO)
agent2 = RuleBasedAgent(player2, game.p2_actions, cooperating=True, log_level=logging.INFO)

game.adjustRewards(
    {
        "positive": 0.1,
        "tick": 0.001,
        "negative": -0.1,
        "win": 1,
        "loss": -1
    }
)

nb_frames = 500
num_epoch = 100
rewards = np.array([0.0, 0.0])
observation = 0
train_start = 1000

r1_list = []
r2_list = []

p1_kills = []
p2_kills = []

for epoch in range(num_epoch):
    for f in range(nb_frames):
        if p.game_over():  # check if the game is over
            p.reset_game()
            break

        state = p.getGameState()

        # obs = p.getScreenRGB()
        action1 = agent1.pick_action(state, rewards, observation)
        action2 = agent2.pick_action(state, rewards, observation)
        rewards = np.array(p.act([action1, action2]))
        agent1.store_reward(rewards)
        agent2.store_reward(rewards)

        observation += 1

    # player 1 rewards
    final_reward1 = np.array([agent1.rewards]).sum()
    print("Player 1: %f" % final_reward1)
    r1_list.append(final_reward1)
    agent1.rewards = []

    # player 2 rewards
    final_reward2 = np.array([agent2.rewards]).sum()
    print("Player 2: %f" % final_reward2)
    r2_list.append(final_reward2)
    agent2.rewards = []

    # save player kill counts
    p1_kills.append(agent1.player.other_player_kill_count)
    p2_kills.append(agent2.player.other_player_kill_count)

    p.reset_game()
    print("End epoch %i" % epoch)

plt.plot(range(num_epoch), r1_list, color='red')
plt.plot(range(num_epoch), r2_list, color='blue')
plt.grid()
plt.title("Reward evolution")
plt.xlabel("Epoch")
plt.ylabel("Reward")
plt.show()

print("Player 1 killed player 2 %i times" % np.sum(np.array(p1_kills)))
print("Player 2 killed player 1 %i times" % np.sum(np.array(p2_kills)))

pygame.quit()
sys.exit()
